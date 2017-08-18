from bs4 import BeautifulSoup


def Table2Parse(table):
    links = []
    rows = []
    newrows = []
    for row in table.find_all("tr"):
        infocol = row.find_all("td", text=True)
        linkcol = row.find_all("a")
        for i in linkcol:
            if i.has_attr('href'):
                links.append(i['href'])
        for i in infocol:
            field = i.get_text()
            if field == '\n':
                field = "None"
            rows.append(field)
    for x in range(5, len(rows), 4):
        if 'None' not in rows[x:x + 4]:
            date = rows[x + 1]
            for j in links:
                if date in j:
                    temp = rows[x:x + 4]
                    temp.append(j)
                    newrows.append(temp)
    return newrows


def Table1Parse(table):
    rows = {}
    for row in table.find_all("tr"):
        col = row.find_all("td")
        key = col[0].get_text()
        field = col[1].get_text()
        if field != '\n' and key != "Syllabus":
            link = col[1].span.a['href']
            rows.update({key: link})
        # if key=="Syllabus":
        #     link="processStudentGeneralDownload()"
        #     rows.update({key:link})
    return rows


def parsethepage(res):
    # with open("dl.html","rb") as f:
    #     res=f.read()
    soup = BeautifulSoup(res.text, "html.parser")
    tables = soup.find_all("table")
    table1 = tables[1]
    table2 = tables[2]
    # list of lists of row-wise details with the last element in each row
    # being the href link
    rows2 = Table2Parse(table2)
    # dictionary with key as the description and value as the download
    # link/function
    rows1 = Table1Parse(table1)
    return rows1, rows2
