const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack') // Импортируем webpack для использования DefinePlugin

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      alias: {
        vue$: 'vue/dist/vue.esm-bundler.js' // Указание на полную сборку Vue
      }
    },
    plugins: [
      new webpack.DefinePlugin({
        // Добавляем флаг для предотвращения предупреждения
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
      }),
    ]
  }
})
