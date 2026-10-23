<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4 ">
      <div class="container ">
        <router-link class="navbar-brand fw-bold " to="/">Placement Portal</router-link>
      </div>
    </nav>

    <div class="container">
      <router-view />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>