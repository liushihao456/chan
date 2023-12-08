const HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    node: {
        __dirname: false,
    },
    entry: './src/index.jsx',
    output: {
        filename: '[name].js',
        path: __dirname + '/dist',
    },
    // target: 'electron-renderer',
    target: 'web',

    resolve: {
        // Add '.js' and '.jsx' as resolvable extensions
        extensions: ['.js', '.jsx', '.json'],
    },

    module: {
        rules: [
            // All files with a '.js' or '.jsx' extension will be handled by 'babel-loader'
            { test: /\.jsx?$/, exclude: /node_modules/, loader: 'babel-loader' },
            // Load '.css' files
            { test: /\.css$/, use: ['style-loader', 'css-loader'] },
            // Web worker '.worker.js' files
            { test: /\.worker\.js$/, loader: 'worker-loader', options: { inline: 'fallback', esModule: false } },
            // "file" loader makes sure those assets get served by WebpackDevServer.
            // When you `import` an asset, you get its (virtual) filename.
            // In production, they would get copied to the `build` folder.
            {
                test: /\.(svg|jpg)$/,
                loader: 'file-loader',
                // exclude: [/\.(js|mjs|jsx|ts|tsx)$/, /\.html$/, /\.json$/, /\.css$/, /\.worker\.js$/],
                options: {
                    name: '[name].[hash:8].[ext]',
                },
            },
        ],
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: './src/index.html',
        }),
    ],

    devServer: {
        hot: true,
        historyApiFallback: {
            // Paths with dots should still use the history fallback.
            // See https://github.com/facebook/create-react-app/issues/387.
            disableDotRule: true,
            index: '/',
        },
    },
};
