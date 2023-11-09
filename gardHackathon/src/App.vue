<script>

import VueDatePicker from '@vuepic/vue-datepicker';
import '@vuepic/vue-datepicker/dist/main.css'
import axios from 'axios'
import PieChart from "@/components/PieChart.vue";
import LineChart from "@/components/LineChart.vue";
import BarChart from "@/components/BarChart.vue";
// import ScatterChart from "@/components/ScatterChart.vue";
import DoughnutChart from "@/components/DoughnutChart.vue";
import BubbleChart from "@/components/BubbleChart.vue";

import AppSpinner from './components/AppSpinner.vue'

export default {
  data() {
    return {
      startDate: 'None',
      endDate: 'None',
      sas: 'None',
      SASs: [
        'devops', 'loans', 'payments', 'wealth'
      ],
      aMod: 'None',
      QGT: 'None',
      QGTs: [
        'CODE_COVERAGE', 'XRAY_DOCKER', 'DUPLICATED_LINES',
        'MAINTAINABILITY_RATING', 'RELIABILITY_RATING',
        'SECURITY_HOTSPOTS_REVIEWED', 'SECURITY_RATING'
      ],
      dUnit: 'None',
      dUnits: [
        'argocd', 'card-guardian-be', 'card-guardian-fe', 'dopo-be',
        'dopo-fe', 'github-sync', 'grafana-app', 'grafana-infra',
        'invest-edge-be', 'invest-edge-fe', 'jenkins', 'jfrog',
        'loan-link-be', 'loan-link-fe', 'mortgages-be', 'mortgages-fe',
        'nexus', 'payapp-be', 'portfolio-man-be', 'portfolio-man-fe',
        'swift-pay-be', 'swift-pay-fe', 'teamcity',
        'transaction-explorer-be', 'transaction-explorer-fe',
        'wealth-wave-be', 'wealth-wave-fe'
      ],
      lang: 'None',
      langs: [
        'PLSQL', 'KOTLIN', 'PYTHON', 'JAVA'
      ],
      env: 'None',
      envs: [
        'PRED', 'INT', 'DEV', 'PRS', 'PROD'
      ],
      platform: 'None',
      platforms: [
        'AZURE', 'OPEN_SHIFT'
      ],
      dataGraph: null,
      blockFlag: false,
      isVisible: false,
      barPlotSuccessByLangDataList: null,
      barPlotSuccessByTypeDataList: null,
      pieChartLangDataList: null,
      successRateGraphDataList: null
    };
  },
  components: {
    AppSpinner,
    BubbleChart,
    DoughnutChart,
    // ScatterChart,
    BarChart,
    LineChart,
    PieChart,
    VueDatePicker,
  },
  computed: {
    aModsFiltered() {
      if (this.sas === 'devops') {
        return ['artifactory', 'cd', 'ci', 'dopo', 'github-sync', 'grafana'];
      } else if (this.sas === 'loans') {
        return ['loan-link', 'mortgages'];
      } else if (this.sas === 'payments') {
        return ['card-guardian', 'payapp', 'swift-pay', 'transaction-explorer'];
      } else if (this.sas === 'wealth') {
        return ['invest-edge', 'portfolio-man', 'wealth-wave'];
      } else {
        return [
          'artifactory', 'card-guardian', 'cd', 'ci', 'dopo', 'github-sync',
          'grafana', 'invest-edge', 'loan-link', 'mortgages', 'payapp',
          'portfolio-man', 'swift-pay', 'transaction-explorer', 'wealth-wave'
        ];
      }
    },
  },
  methods: {
    sendData() {
      this.blockFlag = !this.blockFlag;

      let params;

            if (this.startDate !== 'None' && this.endDate !== 'None')
            {
                var yearS = this.startDate.getFullYear();
                var monthS = ('0' + (this.startDate.getMonth() + 1)).slice(-2); // добавляем 1, так как месяцы начинаются с 0
                var dayS = ('0' + this.startDate.getDate()).slice(-2);

                var yearE = this.endDate.getFullYear();
                var monthE = ('0' + (this.endDate.getMonth() + 1)).slice(-2); // добавляем 1, так как месяцы начинаются с 0
                var dayE = ('0' + this.endDate.getDate()).slice(-2);

                params = {
                    sasName: this.sas,
                    appModuleName: this.aMod,
                    platformName: this.platform,
                    dUnitName: this.dUnit,
                    envName: this.env,
                    startDateName: yearS + '-' + monthS + '-' + dayS,
                    endDateName: yearE + '-' + monthE + '-' + dayE,
                }
            }
            else if (this.startDate === 'None' && this.endDate === 'None'){
                params = {
                    sasName: this.sas,
                    appModuleName: this.aMod,
                    platformName: this.platform,
                    dUnitName: this.dUnit,
                    envName: this.env,
                    startDateName: 'None',
                    endDateName: 'None',
                }
            }
            else if (this.startDate !== 'None' && this.endDate === 'None'){
                yearS = this.startDate.getFullYear();
                monthS = ('0' + (this.startDate.getMonth() + 1)).slice(-2); // добавляем 1, так как месяцы начинаются с 0
                dayS = ('0' + this.startDate.getDate()).slice(-2);

                params = {
                    sasName: this.sas,
                    appModuleName: this.aMod,
                    platformName: this.platform,
                    dUnitName: this.dUnit,
                    envName: this.env,
                    startDateName: yearS + '-' + monthS + '-' + dayS,
                    endDateName: 'None',
                }
            }
            else{
                yearE = this.endDate.getFullYear();
                monthE = ('0' + (this.endDate.getMonth() + 1)).slice(-2); // добавляем 1, так как месяцы начинаются с 0
                dayE = ('0' + this.endDate.getDate()).slice(-2);

                params = {
                    sasName: this.sas,
                    appModuleName: this.aMod,
                    platformName: this.platform,
                    dUnitName: this.dUnit,
                    envName: this.env,
                    startDateName: 'None',
                    endDateName: yearE + '-' + monthE + '-' + dayE,
                }
            }

            axios.get('http://localhost:8000/data/', {
                params: params,
            })

          .then(response => {
            this.dataGraph = response.data;
            console.log(response.data);//Пиши создание графиков тут, используя response.data(Object {"graphname": graph, ...})
            // this.addChartData(response.data.sucessRateGraph.x,response.data.sucessRateGraph.y);
            // console.log(this.chartDataList);
            const data = JSON.parse(JSON.stringify(response.data))
            // console.log(data.successRateGraph)
            // const chartDataList = []
            // const a1 = []
            // const a2 = []
            // for (let key in data) {
            //   console.log(key)
            // }


            this.addBarPlotSuccessByLangDataList(data.barPlotSuccessByLang.x, data.barPlotSuccessByLang.y);
            this.addBarPlotSuccessByTypeDataList(data.barPlotSuccessByType.x, data.barPlotSuccessByType.y);
            this.addPieChartLangDataList(data.pieChartLang.labels, data.pieChartLang.counts)
            this.addSuccessRateGraphDataList(data.successRateGraph.x, data.successRateGraph.y)

            const metrics = []
              console.log(data.metrics)



            this.blockFlag = !this.blockFlag;
          })
          .catch(error => {
            console.error("Error", error)
            this.blockFlag = !this.blockFlag;
          });
      this.isVisible = true;
    },
    addBarPlotSuccessByLangDataList(labels, data) {
      this.barPlotSuccessByLangDataList = ({
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Plot Success by Language',
              backgroundColor: '#2870ed',
              data: data
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    },
    addBarPlotSuccessByTypeDataList(labels, data) {
      this.barPlotSuccessByTypeDataList = ({
        data: {
          labels: labels,
          datasets: [
            {
              label: 'Plot Success by Type',
              backgroundColor: '#2870e3',
              data: data
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
        }
      });
    },
    addPieChartLangDataList(labels, data) {
      this.pieChartLangDataList = ({
        data: {
          labels: labels,
          datasets: [{
            backgroundColor: ['#2870ED', '#B0C4DE', '#008080', '#E0FFFF'],
            data: data
          }]
        },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      labels: {
                          // This more specific font property overrides the global property
                          font: {
                              size: 14,
                              family: "'Poppins', sans-serif",
                              color: 'black'
                          }
                      }
                  }
              },
              borderWidth:0,
              color:'black'
          }
      });
    },
    addSuccessRateGraphDataList(labels, data) {
      this.successRateGraphDataList = ({
        data: {
          labels: labels,
          datasets: [{
            label: 'Success Rate',
            backgroundColor: '#2870ed',
            data: data,
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          pointStyle: false,
          borderWidth: 1,
          fill: true,
          borderColor: '#2870ed'
        }
      });
    },
    eraseAll() {
      this.sas = 'None';
      this.lang = 'None';
      this.aMod = 'None';
      this.platform = 'None';
      this.QGT = 'None';
      this.dUnit = 'None';
      this.env = 'None';
      this.startDate = 'None';
      this.endDate = 'None';

      this.isVisible = false;
    }
  },
};
</script>

<template>
  <AppSpinner v-if="blockFlag"/>

  <header>
    <a href="/">
      <img class="logo" src="./assets/Logo.png" alt="">
    </a>
  </header>

  <div class="page">
    <div class="menu">
      <p class="menuPeriod">Period</p>
      <div class="startDate">
        <VueDatePicker v-model="startDate" class="startDate" :max-date="new Date() "/>
      </div>
      <div class="endDate">
        <VueDatePicker v-model="endDate" locale="cz" class="endDate" :max-date="new Date()"/>
      </div>

      <p class="SASName">SAS</p>
      <div class="SAS">
        <select v-model="sas">
          <option v-for="(sas, index) in SASs" class="SAS" :key="index" :value="sas">{{ sas }}</option>
        </select>
      </div>

      <p class="aModuleName">App Modules</p>
      <div class="aModule">
        <select v-model="aMod">
          <option v-for="(aMod, index) in aModsFiltered" class="SAS" :key="index" :value="aMod">{{ aMod }}</option>
        </select>
      </div>

      <p class="deployUnitName">Deployment Unit</p>
      <div class="deployUnit">
        <select v-model="dUnit">
          <option v-for="(unit, index) in dUnits" class="deployUnit" :key="index" :value="unit">{{ unit }}</option>
        </select>
      </div>

      <p class="envName">Environment</p>
      <div class="env">
        <select v-model="env">
          <option v-for="(env, index) in envs" class="env" :key="index" :value="env">{{ env }}</option>
        </select>
      </div>

      <p class="platformName">Platform</p>
      <div class="platform">
        <select v-model="platform">
          <option v-for="(platform, index) in platforms" class="platform" :key="index" :value="platform">
            {{ platform }}
          </option>
        </select>
      </div>


      <button class="submit" @click="sendData">Submit</button>
      <button class="clear" @click="eraseAll">Clear</button>
    </div>

    <div class="graphs">
      <div v-if="isVisible" class="chart" style="margin-bottom: 0.5%">
        <PieChart v-if="pieChartLangDataList != null" :data="pieChartLangDataList.data"
                  :options="pieChartLangDataList.options">

        </PieChart>
      </div>
      <div v-if="isVisible" class="chart" style="margin-bottom: 0.5%">
        <LineChart v-if="successRateGraphDataList != null" :data="successRateGraphDataList.data"
                   :options="successRateGraphDataList.options">
        </LineChart>
      </div>
      <div v-if="isVisible" class="chart" style="margin-bottom: 0.5%">
        <BarChart v-if="barPlotSuccessByLangDataList != null" :data="barPlotSuccessByLangDataList.data"
                  :options="barPlotSuccessByLangDataList.options">
        </BarChart>
      </div>
      <div v-if="isVisible" class="chart" style="margin-top: 0.5%;width: 48%">
      </div>
      <div v-if="isVisible" class="chart" style="margin-top: 0.5%;width: 48%">
        <BarChart v-if="barPlotSuccessByTypeDataList != null" :data="barPlotSuccessByTypeDataList.data"
                  :options="barPlotSuccessByTypeDataList.options">
        </BarChart>
      </div>
    </div>
  </div>
</template>

<style>
.chart {
  display: flex;
  justify-content: center;
  height: 49%;
  width: 32%;
  background: #E8E8E8;
  border-radius: 1vw;
}

.graphs {
  align-items: center;
  justify-content: space-evenly;
  display: flex;
  flex-wrap: wrap;
  width: 80%;
  max-height: 41vw;
}

header {
  width: 98vw;
  height: 3vw;
  background: #2870ed;
  margin: 1vw;
  border-radius: 2vw;
}

.page {
  display: flex;
}

.logo {
  width: 7vw;
  height: 2.7vw;
  left: 0;
  margin-top: 0.05vw;
}


.menu {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  grid-template-rows: repeat(24, 0.5fr);
  background: #E8E8E8;
  min-height: 5vw;
  max-height: 35.4vw;
  margin-left: 1vw;
  border-radius: 1vw;
  width: 20%;
}

.graphs {
  width: 80%;
}

.menuPeriod {
  grid-column-start: 1;
  grid-column-end: 3;
  grid-row-start: 1;
  grid-row-end: 2;
  margin-top: 1vw;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
}

.startDate {
  grid-column-start: 1;
  grid-column-end: 3;
  grid-row-start: 2;
  grid-row-end: 2;
  text-align: center;
  width: 7vw;
  margin-left: 0.7vw;
  margin-top: 0.45vw;
  font-size: large;
}

.endDate {
  grid-column-start: 4;
  grid-column-end: 6;
  grid-row-start: 2;
  grid-row-end: 2;
  text-align: center;
  width: 7vw;
  margin-top: 0.45vw;
  margin-left: 0.7vw;
}


:root {
  --dp-font-size: 0.8rem;
  --dp-border-radius: 1vw;
  --dp-background-color: #2870ed;
}

.SASName {
  grid-column-start: 1;
  grid-column-end: 5;
  grid-row-start: 3;
  grid-row-end: 4;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
  margin-top: 0.8vw;
}

.SAS {
  grid-row-start: 4;
  grid-row-end: 5;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.aModuleName {
  grid-column-start: 1;
  grid-column-end: 5;
  grid-row-start: 5;
  grid-row-end: 6;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
  margin-top: 0.8vw;
}

.aModule {
  grid-row-start: 6;
  grid-row-end: 7;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.deployUnitName {
  grid-column-start: 1;
  grid-column-end: 5;
  grid-row-start: 7;
  grid-row-end: 8;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
  margin-top: 0.8vw;
}

.deployUnit {
  grid-row-start: 8;
  grid-row-end: 9;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.QGTName {
  grid-column-start: 1;
  grid-column-end: 6;
  grid-row-start: 9;
  grid-row-end: 10;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
  margin-top: 0.8vw;
}

.QGT {
  grid-row-start: 11;
  grid-row-end: 12;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.langName {
  grid-column-start: 1;
  grid-column-end: 6;
  grid-row-start: 12;
  grid-row-end: 13;
  margin-left: 1.4vw;
  padding-top: 0.8vw;
  margin-top: 0.5vw;
}

.lang {
  grid-row-start: 13;
  grid-row-end: 14;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.envName {
  grid-column-start: 1;
  grid-column-end: 6;
  grid-row-start: 9;
  grid-row-end: 10;
  margin-left: 1.4vw;
  padding-top: 0.3vw;
  margin-top: 0.8vw;
}

.env {
  grid-row-start: 10;
  grid-row-end: 11;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

.platformName {
  grid-column-start: 1;
  grid-column-end: 6;
  grid-row-start: 11;
  grid-row-end: 12;
  margin-left: 1.4vw;
  padding-top: 0.8vw;
  margin-top: 0.5vw;
}

.platform {
  grid-row-start: 12;
  grid-row-end: 13;
  margin-top: 0.8vw;
  grid-column-start: 1;
  grid-column-end: 5;
  margin-left: 1.4vw;
  width: 4vw;
}

button {
  background: #2870ed;
  color: #fff;
  border-radius: 2vw;
  border: 0.1vw solid #2870ed;
  cursor: pointer;
  transition: transform 500ms ease;
  margin-top: 1.8vw;
  width: 5.5vw;
  height: 1.9vw;
  font-size: medium;
  font-weight: bold;
  margin-bottom: 1vw;
  font-family: Poppins, sans-serif;
}

button:hover {
  transform: scale(1.1) translateY(-5px);
}


.submit {
  grid-row-start: 13;
  grid-row-end: 14;
  grid-column-start: 2;
  grid-column-end: 3;
  margin-left: 0.7vw;
}

.clear {
  grid-row-start: 13;
  grid-row-end: 14;
  grid-column-start: 4;
  grid-column-end: 5;
  margin-left: 0.7vw;
}

select {
  width: 16.9vw;
  height: 1.3vw;
  font-size: large;
  border-radius: 2vw;
  padding-left: 0.3vw;
  font-family: Poppins, sans-serif;
  background: white;
}

p {
  font-family: Poppins, sans-serif;
  font-size: large;
  font-weight: normal;
}

</style>
