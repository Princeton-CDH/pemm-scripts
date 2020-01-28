global.showIncipitSidebar = () => {
    const sidebarHtml = HtmlService.createHtmlOutputFromFile('incipits')
        .setTitle('Incipits')
        .setWidth(800)

    SpreadsheetApp.getUi().showSidebar(sidebarHtml)
}

global.onOpen = () => {
    /* set up incipit menu */
    SpreadsheetApp.getUi()
        .createMenu('Incipits')
        .addItem('Show sidebar', 'showIncipitSidebar')
        .addToUi()
}

global.checkStars = () => {
    const ui = SpreadsheetApp.getUi()
    
    const selectedRange = SpreadsheetApp.getActiveRange()
    const values = selectedRange.getValues()

    const items = fetchRepos(values[0][0])

    const projects = items
        .map((p:any) => `<li><a href="${p.url}">${p.name}</a></li>`)
        .join('\n')

    return `GitHub repos titled ${values[0][0]} with >= 100 stars:\n${projects}`
}

global.pasteRepos = (location: string) => {
    const selectedRange = SpreadsheetApp.getActiveRange()
    const values = selectedRange.getValues()

    const sheet = SpreadsheetApp.getActiveSheet()
    const range = sheet.getRange(location)
    const items = fetchRepos(values[0][0])

    range.setValues([items.map((p: any) => p.name)])
}

const fetchRepos = (name: string): Array<object> => {
    const query = encodeURIComponent(`"${name}" stars:">=100"`)
    const url = `https://api.github.com/search/repositories?sort=stars&q=${query}`
    const response = UrlFetchApp.fetch(url, {'muteHttpExceptions': true})
    const content = JSON.parse(response.getContentText())
    return content.items
}