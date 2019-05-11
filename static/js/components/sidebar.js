$(document).ready(function () {
    let sidebar = $('#sidebar'),
        content = $('#content'),
        hideSidebarIcon = $('#hideSidebarIcon'),
        showSidebarIcon = $('#showSidebarIcon');

    $('#sidebarToggleBtn').on('click', function () {
        sidebar.toggleClass('active');
        content.toggleClass('active');
        hideSidebarIcon.toggleClass('active');
        showSidebarIcon.toggleClass('active');
    });
});