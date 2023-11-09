<template>
  <Pie :data="data" :options="options"></Pie>
</template>

<script>
import {Pie} from 'vue-chartjs';
import {Chart as ChartJs, ArcElement, Tooltip, Legend} from "chart.js";

ChartJs.register(ArcElement, Tooltip, Legend)
export default {
  name: 'PieChart',
  components: {Pie},
  computed: {
    data() {
      return {
        labels: ['1', '2', '3'],
        datasets: [{
          backgroundColor: ['green', 'red', 'yellow'],
          data: [12, 13, 13]
        }]
      }
    },
    options() {
      return {
        responsive: true,
        maintainAspectRatio: false
      }
    }
  }
}
</script>