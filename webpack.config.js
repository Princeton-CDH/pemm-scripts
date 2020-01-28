const path = require('path')
const GasPlugin = require('gas-webpack-plugin')
const BabelGasPlugin = require('./babel-gas-plugin')

const root = path.resolve(__dirname)

module.exports = {
    mode: 'development',
    context: path.join(root, 'src'),
    entry: {
        main: './main.ts',
        incipit: './incipit.ts'
    },
    devtool: 'none',
    output: {
        filename: '[name].gs',
        path: path.join(root, 'build'),
    },
    resolve: {
        extensions: ['.ts', '.json', '.html'],
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