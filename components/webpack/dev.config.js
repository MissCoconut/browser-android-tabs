const path = require('path')
const webpack = require('webpack')
const productionConfig = require('./prod.config.js')

module.exports = Object.assign({}, productionConfig, {
  mode: 'development',
  devtool: '#inline-source-map'
})
