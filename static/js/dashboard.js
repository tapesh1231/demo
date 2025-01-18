document.getElementById('toggleArrow').addEventListener('click', function() {
    var navbar = $('#subnav');
    var spacer = $('#spacer');
    if (navbar.is(':visible')) {
        navbar.animate({ left: '-200px' }, 500, function() {
            navbar.hide();
        });
        spacer.animate({ width: '0' }, 500);
        this.innerHTML = '&#9654;';
    } else {
        navbar.show().animate({ left: '0' }, 500);
        spacer.animate({ width: '2%' }, 500);
        this.innerHTML = '&#9660;';
    }
});

function showSubnav(section) {
    var subnavLinks = {
        'section1': [
            { text: 'Subsection 1', href: '#subsection1' },
            { text: 'Subsection 2', href: '#subsection2' }
        ],
        'section2': [
            { text: 'Subsection 3', href: '#subsection3' },
            { text: 'Subsection 4', href: '#subsection4' }
        ],
        'section3': [
            { text: 'Subsection 5', href: '#subsection5' },
            { text: 'Subsection 6', href: '#subsection6' }
        ]
    };

    var subnav = $('#subnav');
    var subnavLinksContainer = $('#subnav-links');
    subnavLinksContainer.empty();

    subnavLinks[section].forEach(function(link) {
        subnavLinksContainer.append('<li><a href="' + link.href + '">' + link.text + '</a></li>');
    });

    subnav.show();
}
