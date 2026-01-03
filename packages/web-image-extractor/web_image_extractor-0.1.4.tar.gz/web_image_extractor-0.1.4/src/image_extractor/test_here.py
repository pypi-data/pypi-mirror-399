import web_classes as w
import helpers as h


def test_css_class():
    pass


def test_img_classes() -> (
    dict[str, tuple[set[str], set[str]] | w.ImageFromHTML | w.ImageGetter]
):
    html = w.get_web_text("https://www.squarespace.com/")
    html_img = w.ImageFromHTML()
    imgs = html_img.feed(html, "https://www.squarespace.com/")
    print(len(imgs), imgs[0])
    img = w.ImageGetter()
    img.start(html_img.url, imgs[0].pop(), "imgs/")
    print(img.name)
    return {"imgs": imgs, "html_img": html_img, "img": img}


def test_join_url() -> None:
    ret = h.join_url(
        "https://www.squarespace.com",
        "///universal/styles-compressed/../user-account-core-893a7884c2d25c11-min.en-us.css",
    )
    print(ret)


# test_join_url()
def test_parse_css() -> None:
    print(
        w.CSSParser().parse_css(
            "https://gram.edu",
            "background:url(/_resources/images/_redesign/by-the-numbers-dummy-bg.jpg)",
        )
    )


test_parse_css()
