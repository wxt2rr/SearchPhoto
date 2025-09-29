import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Search from '@/views/Search.vue'
import Folders from '@/views/Folders.vue'
import TimelineView from '@/components/TimelineView.vue'
import LocationView from '@/components/LocationView.vue'
import PeopleView from '@/components/PeopleView.vue'
import StoryGenerator from '@/components/StoryGenerator.vue'
import Settings from '@/views/Settings.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/search',
      name: 'search',
      component: Search
    },
    {
      path: '/folders',
      name: 'folders',
      component: Folders
    },
    {
      path: '/timeline',
      name: 'timeline',
      component: TimelineView
    },
    {
      path: '/location',
      name: 'location',
      component: LocationView
    },
    {
      path: '/people',
      name: 'people',
      component: PeopleView
    },
    {
      path: '/stories',
      name: 'stories',
      component: StoryGenerator
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings
    }
  ]
})

export default router