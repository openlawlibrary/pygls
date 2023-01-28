const path = require('path')

const clientConfig = {
  mode: 'none',
  target: 'webworker',
  entry: {
    client: './src/client.ts'
  },
  output: {
    filename: '[name].js',
    path: path.join(__dirname, 'out'),
    libraryTarget: 'commonjs'
  },
  resolve: {
    mainFields: ['module', 'main'],
    extensions: ['.ts', '.js'],
    fallback: {
      path: require.resolve('path-browserify')
    },
  },
  module: {
    rules: [
      {
        test: /.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader'
          }
        ]
      }
    ]
  },
  externals: {
    vscode: 'commonjs vscode'
  },
  devtool: 'source-map'
}

const serverConfig = {
  mode: 'none',
  target: 'webworker',
  entry: {
    server: './src/server'
  },
  output: {
    filename: '[name].js',
    path: path.join(__dirname, 'out'),
    libraryTarget: 'var',
    library: 'serverExportVar'
  },
  resolve: {
    mainFields: ['module', 'main'],
    extensions: ['.ts', 'js'],
  },
  module: {
    rules: [
      {
        test: /\.ts$/,
        exclude: /node_modules/,
        use: [
          {
            loader: 'ts-loader'
          }
        ]
      },
      {
        test: /\.py$/,
        type: 'asset/source'
      }
    ]
  },
  devtool: 'source-map'
}

module.exports = [clientConfig, serverConfig]