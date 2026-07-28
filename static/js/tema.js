function alternarTema(){

    document.body.classList.toggle(
        "dark-mode"
    );


    localStorage.setItem(
        "tema",
        document.body.classList.contains(
            "dark-mode"
        )
    );

}



window.onload = function(){

    let tema = localStorage.getItem("tema");


    if(tema === "true"){

        document.body.classList.add(
            "dark-mode"
        );

    }

}