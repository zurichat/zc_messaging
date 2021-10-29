/* eslint-env node */
const { merge } = require("webpack-merge")
const singleSpaDefaults = require("webpack-config-single-spa")
const HtmlWebpackPlugin = require("html-webpack-plugin")
const CopyWebpackPlugin = require("copy-webpack-plugin")
const path = require("path")

module.exports = (webpackConfigEnv, argv) => {
  const orgName = "zuri-messaging"
  const defaultConfig = singleSpaDefaults({
    orgName,
    projectName: "root-config",
    webpackConfigEnv,
    argv,
    disableHtmlGeneration: true
  })

  return merge(defaultConfig, {
    //
    externals: {
      jquery: "jQuery"
    },
    // modify the webpack config however you'd like to by adding to this object
    output: {
      path: path.join(__dirname, "..", "dist") // string (default)
    },
    module: {
      rules: [
        {
          test: /\.jpe?g$|\.ico$|\.gif$|\.png$|\.svg$|\.woff$|\.ttf$|\.wav$|\.mp3$/,
          use: {
            loader: "file-loader",
            options: {
              importLoaders: 1,
              modules: {
                name: "[name].[ext]"
              }
            }
          }
        }
      ]
    },
    plugins: [
      new CopyWebpackPlugin({
        patterns: [{ from: "src/assets", to: "assets" }]
      }),
      new HtmlWebpackPlugin({
        inject: false,
        template: "src/index.ejs",
        templateParameters: {
          isLocal: webpackConfigEnv && webpackConfigEnv.isLocal,
          orgName
        }
      })
    ]
  })
}
