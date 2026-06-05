<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({}),
  },
  authors: {
    type: Array,
    default: () => [],
  },
  tags: {
    type: Array,
    default: () => [],
  },
  venues: {
    type: Array,
    default: () => [],
  },
  submitText: {
    type: String,
    default: 'Save',
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['submit', 'cancel'])

const form = reactive({
  title: '',
  abstract: '',
  year: null,
  venue_name: '',
  venue_type: 'conference',
  paper_type: 'article',
  doi: '',
  arxiv_id: '',
  url: '',
  reading_status: 'unread',
  author_names: [],
  tag_names: [],
})

const authorOptions = computed(() => props.authors.map((author) => author.author_name))
const tagOptions = computed(() => props.tags.map((tag) => tag.tag_name))
const venueOptions = computed(() => props.venues.map((venue) => venue.venue_name))

watch(
  () => props.modelValue,
  (paper) => {
    form.title = paper.title || ''
    form.abstract = paper.abstract || ''
    form.year = paper.year || null
    form.venue_name = paper.venue_ref?.venue_name || paper.venue || ''
    form.venue_type = paper.venue_ref?.venue_type || 'conference'
    form.paper_type = paper.paper_type || 'article'
    form.doi = paper.doi || ''
    form.arxiv_id = paper.arxiv_id || ''
    form.url = paper.url || ''
    form.reading_status = paper.reading_status || 'unread'
    form.author_names = paper.authors?.map((author) => author.author_name) || []
    form.tag_names = paper.tags?.map((tag) => tag.tag_name) || []
  },
  { immediate: true, deep: true },
)

function cleanPayload() {
  const payload = {
    title: form.title.trim(),
    abstract: form.abstract.trim() || null,
    year: form.year || null,
    venue_name: form.venue_name.trim() || null,
    venue_type: form.venue_type,
    paper_type: form.paper_type || 'article',
    doi: form.doi.trim() || null,
    arxiv_id: form.arxiv_id.trim() || null,
    url: form.url.trim() || null,
    reading_status: form.reading_status,
    author_names: form.author_names,
    tag_names: form.tag_names,
  }
  return payload
}

function submit() {
  emit('submit', cleanPayload())
}
</script>

<template>
  <el-form class="paper-form" label-position="top" @submit.prevent="submit">
    <el-form-item label="Title" required>
      <el-input v-model="form.title" placeholder="Paper title" />
    </el-form-item>

    <div class="form-grid">
      <el-form-item label="Year">
        <el-input-number v-model="form.year" :min="1900" :max="2100" controls-position="right" />
      </el-form-item>
      <el-form-item label="Reading Status">
        <el-select v-model="form.reading_status">
          <el-option label="Unread" value="unread" />
          <el-option label="Reading" value="reading" />
          <el-option label="Finished" value="finished" />
          <el-option label="Archived" value="archived" />
        </el-select>
      </el-form-item>
      <el-form-item label="Paper Type">
        <el-input v-model="form.paper_type" placeholder="article" />
      </el-form-item>
    </div>

    <div class="form-grid">
      <el-form-item label="Venue">
        <el-select
          v-model="form.venue_name"
          allow-create
          clearable
          filterable
          placeholder="Conference / journal"
        >
          <el-option v-for="venue in venueOptions" :key="venue" :label="venue" :value="venue" />
        </el-select>
      </el-form-item>
      <el-form-item label="Venue Type">
        <el-select v-model="form.venue_type">
          <el-option label="Conference" value="conference" />
          <el-option label="Journal" value="journal" />
          <el-option label="Workshop" value="workshop" />
          <el-option label="Preprint" value="preprint" />
        </el-select>
      </el-form-item>
    </div>

    <div class="form-grid">
      <el-form-item label="DOI">
        <el-input v-model="form.doi" placeholder="10.xxxx/xxxxx" />
      </el-form-item>
      <el-form-item label="arXiv ID">
        <el-input v-model="form.arxiv_id" placeholder="2501.00001" />
      </el-form-item>
    </div>

    <el-form-item label="URL">
      <el-input v-model="form.url" placeholder="https://..." />
    </el-form-item>

    <el-form-item label="Authors">
      <el-select
        v-model="form.author_names"
        allow-create
        clearable
        filterable
        multiple
        placeholder="Select or type author names"
      >
        <el-option v-for="author in authorOptions" :key="author" :label="author" :value="author" />
      </el-select>
    </el-form-item>

    <el-form-item label="Tags">
      <el-select
        v-model="form.tag_names"
        allow-create
        clearable
        filterable
        multiple
        placeholder="Select or type tags"
      >
        <el-option v-for="tag in tagOptions" :key="tag" :label="tag" :value="tag" />
      </el-select>
    </el-form-item>

    <el-form-item label="Abstract">
      <el-input v-model="form.abstract" :rows="5" type="textarea" />
    </el-form-item>

    <div class="form-actions">
      <el-button @click="emit('cancel')">Cancel</el-button>
      <el-button type="primary" :loading="loading" @click="submit">{{ submitText }}</el-button>
    </div>
  </el-form>
</template>
