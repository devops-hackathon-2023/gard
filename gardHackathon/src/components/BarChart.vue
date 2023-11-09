<template>
  <Bar :data="data" :options="options"/>
</template>

<script lang="ts">
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale
} from 'chart.js'
import {Bar} from 'vue-chartjs'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

export default {
  name: 'BarChart',
  components: {
    Bar
  },
  computed: {
    data() {
      return {
        labels: [],
        datasets: []
      }
    },
    options() {
      return {}
    }
  }
}
</script>
