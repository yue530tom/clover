<template>
  <el-select
    v-model="team"
    @change="selectTeam"
    placeholder="请选择团队"
    clearable
  >
    <el-option
      v-for="team in teams"
      :key="team.value"
      :label="team.label"
      :value="team.value">
    </el-option>
  </el-select>
</template>

<script>
export default {
  data () {
    return {
      team: '',
      teams: []
    }
  },
  mounted () {
    this.getTeam()
  },
  methods: {
    getTeam () {
      this.$axios({
        url: '/api/v1/environment/aggregate',
        method: 'post',
        data: JSON.stringify({
          type: 'team',
          key: 'team'
        }),
        headers: {
          'Content-Type': 'application/json;'
        }
      }).then((res) => {
        for (const index in res.data.data) {
          this.teams.push({
            label: res.data.data[index]._id,
            value: res.data.data[index]._id
          })
        }
      })
    },
    selectTeam (value) {
      this.team = value
      this.$emit('selectedTeam', this.team)
    }
  }
}
</script>
