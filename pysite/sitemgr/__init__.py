"""
Module of the SiteManager.


All sites and pages are dynamically read from the filesystem.

Sites are located inside a specific directory that is set in class 
attribute :attr:`models.Sites.SITES_DIR` on application start. Each site
is a subdirectory; its master configuration settings are read from
a YAML file with the same name, which is also stored in the SITES_DIR.
User-defined settings are stored in the YAML file `rc.yaml`, which
is located inside the subdirectory of the site.

Each site contains a subdirectory "assets" which is intended to contain
static assets like CSS files and images. It is published via a static
route in Pyramid.

Each site also contains a subdirectory "content". This directory
contains the published pages of the site.

A page needs two files: one with extension ".jinja2". This contains the content
and the filename is used in the page's URL. The second needed file is a file
with the same name and extension ".yaml". It contains the page's settings.

See :mod:`~.pysite.sitemgr.models` for a description how the SiteManager connects to the resource tree.

See :mod:`~.pysite.sitemgr.page` for details about creating pages and linking.
"""
