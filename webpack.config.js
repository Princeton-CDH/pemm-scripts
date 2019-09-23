const path = require('path')
const GasPlugin = require('gas-webpack-plugin')
const BabelGasPlugin = require('./babel-gas-plugin')

const root = path.resolve(__dirname)

module.exports = {
    mode: 'development',
    context: path.join(root, 'src'),
    entry: path.join(root, 'src', 'main.ts'),
    devtool: 'none',
    output: {
        filename: 'build.gs',
        path: path.join(root, 'build'),
    },
    resolve: {
        extensions: ['.ts', '.json'],
        modules: [root, 'node_modules']
    },
    module: {
        rules: [
            {
                test: /\.ts$/,
                use: 'ts-loader',
                exclude: /node_modules/,
            },
        ]
    },
    plugins: [
        new GasPlugin(),
        new BabelGasPlugin(),
    ]
}