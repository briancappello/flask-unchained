const fs = require('fs')
const path = require('path')
const webpack = require('webpack')

const ExtractTextPlugin = require('extract-text-webpack-plugin')
const ManifestPlugin = require('webpack-manifest-plugin')

const PROJECT_ROOT = path.resolve(path.join(__dirname, '..'))
const ASSETS_ROOT = path.join(PROJECT_ROOT, 'assets')
const SCRIPTS_ROOT = path.join(ASSETS_ROOT, 'scripts')
const STYLES_ROOT = path.join(ASSETS_ROOT, 'styles')
const OUTPUT_PATH = path.join(PROJECT_ROOT, 'static', 'assets')


module.exports = {
  entry: {
    ...getEntryPoints(SCRIPTS_ROOT, 'index.js'),
    ...getEntryPoints(STYLES_ROOT, 'main.scss'),
  },
  output: {
    path: OUTPUT_PATH,
    publicPath: '/assets/',
    filename: '[name].[chunkhash].js',
    chunkFilename: '[id].[chunkhash].js'
  },
  resolve: {
    modules: [SCRIPTS_ROOT, STYLES_ROOT, 'node_modules'],
    extensions: ['.js'],
    mainFields: [
      'browser',
      'jsnext:main',
      'main',
    ]
  },
  module: {
    loaders: [
      {
        test: /\.js$/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: [
              ['env', {
                debug: true,
                modules: false,
                useBuiltIns: true,
                targets: {
                  browsers: [
                    '> 1%',
                    'last 2 versions',
                    'Firefox ESR',
                  ],
                },
              }],
            ],
          },
        },
        // include: SCRIPTS_ROOT,
        // exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        loader: ExtractTextPlugin.extract(
          'style-loader',
          'css-loader',
          'resolve-url-loader',
        ),
      },
      {
        test: /\.(sass|scss)$/,
        use: ExtractTextPlugin.extract({
          fallback: 'style-loader',
          use: [
            'css-loader',
            'resolve-url-loader',
            {
              loader: 'sass-loader',
              options: {
                sourceMap: true,
                includePaths: [STYLES_ROOT],
              },
            },
          ],
        }),
      },
      {
        test: /\.(gif|ico|jpg|jpeg|png)$/,
        use: [
          'file-loader',
          {
            loader: 'image-webpack-loader',
            options: {
              gifsicle: { interlaced: false },
              mozjpeg: { progressive: true },
              optipng: { optimizationLevel: 7 },
              pngquant: { quality: '65-90', speed: 4 },
            },
          },
        ],
      },
      {
        test: /\.(eot|svg|ttf|woff|woff2)$/,
        use: 'file-loader',
      },
    ],
  },
  plugins: [
    new ExtractTextPlugin('[name].[chunkhash].css'),
    new ManifestPlugin({
      writeToFileEmit: true,
    }),

    // FIXME this is for BC until resolve-url-loader upgrades their shit
    new webpack.LoaderOptionsPlugin({
      options: {
        resolveUrlLoader: {
          root: ASSETS_ROOT,
          includeRoot: true,
        },
      },
    }),
  ],
}


function fileExists(filepath) {
  try {
    fs.accessSync(filepath)
    return true
  } catch (e) {
    return false
  }
}

function getEntryPoints(rootDir, filename) {
  /**
   * Searches `rootDir` for child directories containing `filename`, and
   * returns them as entry points
   */
  return fs.readdirSync(rootDir)
    // find directories in rootDir
    .map(name => path.resolve(rootDir, name))
    .filter(filepath => fs.lstatSync(filepath).isDirectory())

    // find only the ones containing filename
    .map(name => path.resolve(name, filename))
    .filter(fileExists)

    // convert to an object of entry-point-name: filepath
    .reduce((acc, filename) => {
      const parts = path.dirname(filename).split(path.sep)
      acc[parts[parts.length - 1]] = filename
      return acc
    }, {})
}
