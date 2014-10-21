function getBaseRowHtml(rowJson){
        var trHtml="<tr>";
        for(i in rowJson)
        {
          trHtml+="<td>"+row[i]+"</td>"
        }
        trHtml+="</tr>"
        return trHtml;
    }
