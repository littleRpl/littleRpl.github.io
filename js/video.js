var ifchang = $(".detailsC").find("iframe");
			

		var lianjie=new Array();
	
	
 for (var i=0;i<ifchang.length;i++) {
	 

	 
    var tdArr = ifchang.eq(i).attr("src");
	
	

		var hg=tdArr+";";
		 
		
		 lianjie+=hg;
		 
		 }
 
  var cd=lianjie.length;
if(cd!=0){
  

  lianjie=lianjie.substring(0,cd-1);
lianjie=lianjie.split(';'); 
var can="";
$.each(lianjie, function(index, value){

 
    can+="<video controls='controls' style='width:100%'><source src='"+value+"' type='video/ogg' /></video>";
});

$(".detailsC").find("iframe").remove();

var nei=$(".detailsC").html();


var zhi=can+nei;

$(".detailsC").html(zhi);
 
  
	
}