const babel = require('@babel/core')
const OriginalSource = require('webpack-sources').OriginalSource

/**
 * An extremely simple webpack plugin that runs babel once in order to 
 * use babel-preset-gas to transform property accessors.
 * 
 * Without this plugin, imported modules or files (e.g. json) will not
 * be accessible using the default dot syntax in javascript.
 * https://github.com/fossamagna/babel-preset-gas
 * 
 * Rewritten from https://github.com/simlrh/babel-webpack-plugin to use
 * webpack's hooks API and babel v7.
 */
module.exports = class BabelGasPlugin {
    apply(compiler) {
        compiler.hooks.compilation.tap('BabelGasPlugin', compilation => {
            compilation.hooks.optimizeChunkAssets.tap('BabelGasPlugin', chunks => {
                let files = []
                chunks.forEach(chunk => files.push(...chunk.files))
                files.forEach(file => {
                    const asset = compilation.assets[file]
                    const result = babel.transform(asset.source(), { presets: ['gas' ]})
                    compilation.assets[file] = new OriginalSource(result.code, file)
                })
            })
        })
    }
}