export type AdrRecord = {
  schemaVersion: number
  id: string
  slug: string
  title: string
  status: string
  date: string
  category: string
  tags: string[]
  keywords: string[]
  supersedes: string[]
  supersededBy: string[]
  markdown: string
  searchText: string
  sourcePath: string
}

export type SearchState = {
  query: string
  status: string
  category: string
  tag: string
  order: 'newest' | 'oldest'
}
