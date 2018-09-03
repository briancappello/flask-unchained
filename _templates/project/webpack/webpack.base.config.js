const path = require('path')
const webpack = require('webpack')

const ExtractTextPlugin = require('extract-text-webpack-plugin')
const ManifestPlugin = require('webpack-manifest-plugin')

const PROJECT_ROOT = path.resolve(__dirname)
const ASSETS_ROOT = path.join(PROJECT_ROOT, 'assets')
const SCRIPTS_ROOT = path.join(ASSETS_ROOT, 'scripts')
const STYLES_ROOT = path.join(ASSETS_ROOT, 'styles')
const OUTPUT_PATH = path.join(PROJECT_ROOT, 'static', 'assets')

process.traceDeprecation = true

module.exports = (options) => ({
  devtool: options.devtool,
  target: 'web',
  performance: options.performance || {},
  resolve: {
    modules: [SCRIPTS_ROOT, STYLES_ROOT, 'node_modules'],
    extensions: ['.js', '.jsx'],
    mainFields: [
      'browser',
      'jsnext:main',
      'main',
    ],
  },
  entry: options.entry,
  output: Object.assign({
    path: OUTPUT_PATH,
    publicPath: '/assets/',
    filename: '[name].[chunkhash].js',
    chunkFilename: '[id].[chunkhash].js',
  }, options.output),
  module: {
    rules: [
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
  plugins: options.plugins.concat([
    new webpack.ProvidePlugin({
      fetch: 'imports?this=>global!exports?global.fetch!whatwg-fetch',
    }),

    new webpack.DefinePlugin({
      'process.env': {
        NODE_ENV: JSON.stringify(process.env.NODE_ENV),
      },
    }),

    new webpack.NamedModulesPlugin(),

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
  ]),
})
