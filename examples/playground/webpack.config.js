const path = require('path')
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin')

// Configuration for the language client
/**@type {import('webpack').Configuration}*/
const clientConfig = {
  target: 'web',
  entry: './src/client.ts',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'client.js',
  },
  devtool: 'source-map',
  resolve: {
    extensions: ['.ts', '.js'],
    mainFields: ['module', 'main'],
    fallback: {
      path: require.resolve('path-browserify')
    }
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader',
          }
        ]
      },
      {
        test: /\.css$/,
        use: ["style-loader", "css-loader"]
      },
      {
        test: /\.ttf$/,
        use: ["file-loader"]
      },
      {
        test: /\.py$/,
        type: 'asset/source'
      }
    ]
  },
  plugins: [
    new MonacoWebpackPlugin({
      languages: ['python']
    })
  ]
}

// Configuration for the language server glue code.
/**@type {import('webpack').Configuration}*/
const serverConfig = {
  target: 'webworker',
  entry: './src/serverWorker.ts',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'serverWorker.js',
  },
  devtool: 'source-map',
  resolve: {
    extensions: ['.ts', '.js'],
    mainFields: ['module', 'main'],
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader',
          }
        ]
      }
    ]
  }
}

module.exports = [clientConfig, serverConfig]
