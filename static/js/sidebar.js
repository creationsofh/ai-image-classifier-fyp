function toggleSidebar(){

    const sidebar =
    document.getElementById("sidebar");

    const main =
    document.getElementById("main");

    const overlay =
    document.getElementById("mobileOverlay");

    sidebar.classList.toggle("collapsed");

    main.classList.toggle("expanded");

    overlay.classList.toggle("active");

}