"""模块 D：项目协作路由（项目、成员、任务、评论、活动日志）"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from database import get_db
from models import (
    Project,
    ProjectMember,
    ReadingTask,
    TaskAssignment,
    Comment,
    ActivityLog,
    Paper,
    User,
)
from routers.auth import get_current_user
from schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectOut,
    ProjectDetailOut,
    MemberAdd,
    MemberUpdate,
    MemberOut,
    TaskCreate,
    TaskUpdate,
    TaskStatusUpdate,
    TaskOut,
    TaskDetailOut,
    CommentCreate,
    CommentOut,
    ActivityLogOut,
    DashboardStats,
)

router = APIRouter()


def _log_activity(
    db: Session,
    user_id: int,
    action_type: str,
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    description: Optional[str] = None,
):
    db.add(
        ActivityLog(
            user_id=user_id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )
    )


# ============================================================
# Dashboard
# ============================================================
@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取 Dashboard 统计数据。"""
    paper_count = db.query(func.count(Paper.paper_id)).scalar()
    from models import Note

    note_count = db.query(func.count(Note.note_id)).scalar()
    project_count = db.query(func.count(Project.project_id)).scalar()
    pending_task_count = (
        db.query(func.count(TaskAssignment.task_id))
        .filter(TaskAssignment.status.in_(["todo", "reading"]))
        .scalar()
    )
    recent_papers = (
        db.query(Paper)
        .order_by(Paper.created_at.desc())
        .limit(10)
        .all()
    )
    recent_activities = (
        db.query(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(10)
        .all()
    )
    # 高频标签
    from models import Tag

    top_tags_raw = (
        db.query(
            Tag.tag_name,
            func.count("paper_tags.c.paper_id").label("cnt"),
        )
        .join(Tag.papers)
        .group_by(Tag.tag_id)
        .order_by(func.count("paper_tags.c.paper_id").desc())
        .limit(10)
        .all()
    )
    top_tags = [{"tag_name": tag_name, "count": cnt} for tag_name, cnt in top_tags_raw]

    return DashboardStats(
        paper_count=paper_count or 0,
        note_count=note_count or 0,
        project_count=project_count or 0,
        pending_task_count=pending_task_count or 0,
        recent_papers=[
            {
                "paper_id": p.paper_id,
                "title": p.title,
                "year": p.year,
                "created_at": str(p.created_at) if p.created_at else None,
            }
            for p in recent_papers
        ],
        recent_activities=[
            ActivityLogOut.model_validate(a) for a in recent_activities
        ],
        top_tags=top_tags,
    )


# ============================================================
# 项目管理
# ============================================================
@router.get("/projects", response_model=list[ProjectDetailOut])
def list_projects(
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """列出所有项目。"""
    projects = (
        db.query(Project)
        .options(joinedload(Project.members))
        .order_by(Project.created_at.desc())
        .all()
    )
    result = []
    for p in projects:
        paper_count = 0
        task_count = len(p.reading_tasks) if p.reading_tasks else 0
        result.append(
            ProjectDetailOut(
                project_id=p.project_id,
                project_name=p.project_name,
                description=p.description,
                owner_id=p.owner_id,
                created_at=str(p.created_at) if p.created_at else None,
                member_count=len(p.members) if p.members else 0,
                paper_count=paper_count,
                task_count=task_count,
            )
        )
    return result


@router.post("/projects", response_model=ProjectOut)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建科研项目。"""
    project = Project(
        project_name=data.project_name,
        description=data.description,
        owner_id=current_user.user_id,
    )
    db.add(project)
    db.flush()
    # 创建者自动成为 admin 成员
    db.add(
        ProjectMember(
            project_id=project.project_id,
            user_id=current_user.user_id,
            role="admin",
        )
    )
    _log_activity(
        db,
        current_user.user_id,
        "CREATE_PROJECT",
        "project",
        project.project_id,
        f"Created project '{project.project_name}'",
    )
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取项目详情。"""
    p = (
        db.query(Project)
        .options(joinedload(Project.members), joinedload(Project.reading_tasks))
        .filter(Project.project_id == project_id)
        .first()
    )
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectDetailOut(
        project_id=p.project_id,
        project_name=p.project_name,
        description=p.description,
        owner_id=p.owner_id,
        created_at=str(p.created_at) if p.created_at else None,
        member_count=len(p.members) if p.members else 0,
        paper_count=0,
        task_count=len(p.reading_tasks) if p.reading_tasks else 0,
    )


@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新项目信息。"""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(p, key, value)

    _log_activity(
        db,
        current_user.user_id,
        "UPDATE_PROJECT",
        "project",
        project_id,
        f"Updated project '{p.project_name}'",
    )
    db.commit()
    db.refresh(p)
    return p


@router.delete("/projects/{project_id}")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除项目。"""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(p)
    _log_activity(
        db,
        current_user.user_id,
        "DELETE_PROJECT",
        "project",
        project_id,
        f"Deleted project '{p.project_name}'",
    )
    db.commit()
    return {"message": "Project deleted"}


# ============================================================
# 成员管理
# ============================================================
@router.get("/projects/{project_id}/members", response_model=list[MemberOut])
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """列出项目成员。"""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    return [
        MemberOut(
            user_id=m.user_id,
            username=m.user_info.username if m.user_info else "",
            role=m.role,
            joined_at=str(m.joined_at) if m.joined_at else None,
        )
        for m in p.members
    ]


@router.post("/projects/{project_id}/members", response_model=MemberOut)
def add_member(
    project_id: int,
    data: MemberAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """添加项目成员。"""
    p = db.query(Project).filter(Project.project_id == project_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    user = db.query(User).filter(User.user_id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == data.user_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")

    if data.role not in ("admin", "member", "viewer"):
        raise HTTPException(status_code=400, detail="Role must be admin, member, or viewer")

    pm = ProjectMember(project_id=project_id, user_id=data.user_id, role=data.role)
    db.add(pm)
    _log_activity(
        db,
        current_user.user_id,
        "ADD_MEMBER",
        "project",
        project_id,
        f"Added user {user.username} as {data.role} to project '{p.project_name}'",
    )
    db.commit()
    db.refresh(pm)
    return MemberOut(
        user_id=user.user_id,
        username=user.username,
        role=pm.role,
        joined_at=str(pm.joined_at) if pm.joined_at else None,
    )


@router.put("/projects/{project_id}/members/{user_id}", response_model=MemberOut)
def update_member_role(
    project_id: int,
    user_id: int,
    data: MemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新成员角色。"""
    if data.role not in ("admin", "member", "viewer"):
        raise HTTPException(status_code=400, detail="Role must be admin, member, or viewer")

    pm = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
    if not pm:
        raise HTTPException(status_code=404, detail="Member not found")

    pm.role = data.role
    _log_activity(
        db,
        current_user.user_id,
        "UPDATE_MEMBER_ROLE",
        "project",
        project_id,
        f"Updated user {user_id} role to {data.role}",
    )
    db.commit()
    db.refresh(pm)
    user = db.query(User).filter(User.user_id == user_id).first()
    return MemberOut(
        user_id=user_id,
        username=user.username if user else "",
        role=pm.role,
        joined_at=str(pm.joined_at) if pm.joined_at else None,
    )


@router.delete("/projects/{project_id}/members/{user_id}")
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """移除项目成员。"""
    pm = (
        db.query(ProjectMember)
        .filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        .first()
    )
    if not pm:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(pm)
    _log_activity(
        db,
        current_user.user_id,
        "REMOVE_MEMBER",
        "project",
        project_id,
        f"Removed user {user_id} from project",
    )
    db.commit()
    return {"message": "Member removed"}


# ============================================================
# 阅读任务管理
# ============================================================
@router.get("/tasks", response_model=list[TaskDetailOut])
def list_tasks(
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    assignee_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """列出阅读任务。"""
    query = (
        db.query(ReadingTask)
        .options(
            joinedload(ReadingTask.assignments).joinedload(TaskAssignment.user),
            joinedload(ReadingTask.paper),
            joinedload(ReadingTask.assigner),
        )
    )

    if project_id:
        query = query.filter(ReadingTask.project_id == project_id)
    if status:
        query = query.join(ReadingTask.assignments).filter(
            TaskAssignment.status == status
        )
    if assignee_id:
        query = query.join(ReadingTask.assignments).filter(
            TaskAssignment.user_id == assignee_id
        )

    tasks = query.order_by(ReadingTask.created_at.desc()).all()
    result = []
    for t in tasks:
        assignees = [
            MemberOut(
                user_id=a.user_id,
                username=a.user.username if a.user else "",
                role=a.status,
                joined_at=str(a.finished_at) if a.finished_at else None,
            )
            for a in t.assignments
        ]
        result.append(
            TaskDetailOut(
                task_id=t.task_id,
                project_id=t.project_id,
                paper_id=t.paper_id,
                assigned_by=t.assigned_by,
                title=t.title,
                task_description=t.task_description,
                deadline=str(t.deadline) if t.deadline else None,
                created_at=str(t.created_at) if t.created_at else None,
                paper_title=t.paper.title if t.paper else "",
                assigner_name=t.assigner.username if t.assigner else "",
                assignees=assignees,
            )
        )
    return result


@router.post("/tasks", response_model=TaskDetailOut)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建阅读任务。"""
    # 验证项目存在
    project = db.query(Project).filter(Project.project_id == data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 验证论文存在
    paper = db.query(Paper).filter(Paper.paper_id == data.paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    from datetime import date

    deadline = None
    if data.deadline:
        try:
            deadline = date.fromisoformat(data.deadline)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format, use YYYY-MM-DD")

    task = ReadingTask(
        project_id=data.project_id,
        paper_id=data.paper_id,
        assigned_by=current_user.user_id,
        title=data.title,
        task_description=data.task_description,
        deadline=deadline,
    )
    db.add(task)
    db.flush()

    # 分配任务给指定成员
    for uid in data.assignee_ids:
        user = db.query(User).filter(User.user_id == uid).first()
        if user:
            db.add(
                TaskAssignment(
                    task_id=task.task_id,
                    user_id=uid,
                    status="todo",
                )
            )

    _log_activity(
        db,
        current_user.user_id,
        "CREATE_TASK",
        "task",
        task.task_id,
        f"Created task '{task.title}' for paper '{paper.title}'",
    )
    db.commit()
    db.refresh(task)

    # 重新加载
    task = (
        db.query(ReadingTask)
        .options(
            joinedload(ReadingTask.assignments).joinedload(TaskAssignment.user),
            joinedload(ReadingTask.paper),
            joinedload(ReadingTask.assigner),
        )
        .filter(ReadingTask.task_id == task.task_id)
        .first()
    )
    assignees = [
        MemberOut(
            user_id=a.user_id,
            username=a.user.username if a.user else "",
            role=a.status,
        )
        for a in task.assignments
    ]
    return TaskDetailOut(
        task_id=task.task_id,
        project_id=task.project_id,
        paper_id=task.paper_id,
        assigned_by=task.assigned_by,
        title=task.title,
        task_description=task.task_description,
        deadline=str(task.deadline) if task.deadline else None,
        created_at=str(task.created_at) if task.created_at else None,
        paper_title=task.paper.title if task.paper else "",
        assigner_name=task.assigner.username if task.assigner else "",
        assignees=assignees,
    )


@router.get("/tasks/{task_id}", response_model=TaskDetailOut)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取任务详情。"""
    t = (
        db.query(ReadingTask)
        .options(
            joinedload(ReadingTask.assignments).joinedload(TaskAssignment.user),
            joinedload(ReadingTask.paper),
            joinedload(ReadingTask.assigner),
        )
        .filter(ReadingTask.task_id == task_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    assignees = [
        MemberOut(
            user_id=a.user_id,
            username=a.user.username if a.user else "",
            role=a.status,
            joined_at=str(a.finished_at) if a.finished_at else None,
        )
        for a in t.assignments
    ]
    return TaskDetailOut(
        task_id=t.task_id,
        project_id=t.project_id,
        paper_id=t.paper_id,
        assigned_by=t.assigned_by,
        title=t.title,
        task_description=t.task_description,
        deadline=str(t.deadline) if t.deadline else None,
        created_at=str(t.created_at) if t.created_at else None,
        paper_title=t.paper.title if t.paper else "",
        assigner_name=t.assigner.username if t.assigner else "",
        assignees=assignees,
    )


@router.put("/tasks/{task_id}", response_model=TaskDetailOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新任务信息。"""
    t = (
        db.query(ReadingTask)
        .options(
            joinedload(ReadingTask.assignments),
        )
        .filter(ReadingTask.task_id == task_id)
        .first()
    )
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = data.model_dump(exclude_unset=True)
    assignee_ids = update_data.pop("assignee_ids", None)
    for key, value in update_data.items():
        if key == "deadline" and value:
            from datetime import date
            try:
                value = date.fromisoformat(value)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format")
        setattr(t, key, value)

    if assignee_ids is not None:
        # 清除现有分配
        for a in t.assignments:
            db.delete(a)
        db.flush()
        # 添加新分配
        for uid in assignee_ids:
            db.add(TaskAssignment(task_id=task_id, user_id=uid, status="todo"))

    _log_activity(
        db,
        current_user.user_id,
        "UPDATE_TASK",
        "task",
        task_id,
        f"Updated task '{t.title}'",
    )
    db.commit()
    # 重新加载
    return get_task(task_id, db, current_user)


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除任务。"""
    t = db.query(ReadingTask).filter(ReadingTask.task_id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(t)
    _log_activity(
        db,
        current_user.user_id,
        "DELETE_TASK",
        "task",
        task_id,
        f"Deleted task '{t.title}'",
    )
    db.commit()
    return {"message": "Task deleted"}


@router.put("/tasks/{task_id}/status", response_model=TaskDetailOut)
def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新任务状态（当前用户的任务状态）。"""
    if data.status not in ("todo", "reading", "done", "reported"):
        raise HTTPException(
            status_code=400,
            detail="Status must be todo, reading, done, or reported",
        )

    # 更新当前用户在该任务中的状态
    assignment = (
        db.query(TaskAssignment)
        .filter(
            TaskAssignment.task_id == task_id,
            TaskAssignment.user_id == current_user.user_id,
        )
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Task assignment not found for current user")

    old_status = assignment.status
    assignment.status = data.status
    if data.status in ("done", "reported"):
        from datetime import datetime
        assignment.finished_at = datetime.utcnow()

    _log_activity(
        db,
        current_user.user_id,
        "UPDATE_TASK_STATUS",
        "task",
        task_id,
        f"Changed task status from '{old_status}' to '{data.status}'",
    )
    db.commit()
    return get_task(task_id, db, current_user)


# ============================================================
# 评论管理
# ============================================================
@router.post("/comments", response_model=CommentOut)
def create_comment(
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """创建评论。"""
    if data.target_type not in ("paper", "note", "task"):
        raise HTTPException(status_code=400, detail="target_type must be paper, note, or task")

    comment = Comment(
        user_id=current_user.user_id,
        target_type=data.target_type,
        target_id=data.target_id,
        content=data.content,
    )
    db.add(comment)
    _log_activity(
        db,
        current_user.user_id,
        "ADD_COMMENT",
        data.target_type,
        data.target_id,
        f"Commented on {data.target_type} #{data.target_id}",
    )
    db.commit()
    db.refresh(comment)
    return CommentOut(
        comment_id=comment.comment_id,
        user_id=comment.user_id,
        username=current_user.username,
        target_type=comment.target_type,
        target_id=comment.target_id,
        content=comment.content,
        created_at=str(comment.created_at) if comment.created_at else None,
    )


@router.get("/comments", response_model=list[CommentOut])
def list_comments(
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """列出评论。"""
    query = db.query(Comment).options(joinedload(Comment.user))
    if target_type:
        query = query.filter(Comment.target_type == target_type)
    if target_id:
        query = query.filter(Comment.target_id == target_id)
    comments = query.order_by(Comment.created_at.desc()).all()
    return [
        CommentOut(
            comment_id=c.comment_id,
            user_id=c.user_id,
            username=c.user.username if c.user else "",
            target_type=c.target_type,
            target_id=c.target_id,
            content=c.content,
            created_at=str(c.created_at) if c.created_at else None,
        )
        for c in comments
    ]


# ============================================================
# 活动日志
# ============================================================
@router.get("/activity-logs", response_model=list[ActivityLogOut])
def list_activity_logs(
    project_id: Optional[int] = None,
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """列出活动日志。"""
    query = (
        db.query(ActivityLog)
        .options(joinedload(ActivityLog.user))
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    logs = query.all()
    return [
        ActivityLogOut(
            log_id=a.log_id,
            user_id=a.user_id,
            username=a.user.username if a.user else "",
            action_type=a.action_type,
            target_type=a.target_type,
            target_id=a.target_id,
            description=a.description,
            created_at=str(a.created_at) if a.created_at else None,
        )
        for a in logs
    ]
