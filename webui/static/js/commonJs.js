function getBaseRowHtml(rowJson){
        var trHtml="<tr>";
        for(i in rowJson)
        {
          trHtml+="<td>"+row[i]+"</td>"
        }
        trHtml+="</tr>"
        return trHtml;
    }

//diaozhatian de fangfa
function fillFrom(json,form){
  for(i in json)
  {
    if(!fillCheckBox(name, json[i], form).length)
    {
       $('[name="'+i+'"]',form).val(json[i])
    }
  }
}
function fillCheckBox(name, value, form){
			var cBox = $('input[name="'+name+'"][type=radio], input[name="'+name+'"][type=checkbox]', form);
			cBox.prop('checked',false);
			cBox.each(function(){
				var f = $(this);
				if (f.val() == String(val)){
					f.prop('checked',true);
				}
			});
			return cBox;
		}
//GetUrlRequest
function getUrlRequest(url){
    var Request = new Object;
    if(url.indexOf("?")!=-1)
    {
    　　var str = url.substr(url.indexOf("?")+1)　//去掉?号
    　　strs= str.split("&");
    　　for(i=0;i<strs.length;i++)
    　　{
    　　 　 Request[strs[i].split("=")[0]]=unescape(strs[ i].split("=")[1]);
    　　}
    }
    return Request;
}