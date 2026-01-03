import time
import sys
from DrissionPage import ChromiumPage,Chromium,ChromiumOptions

url = ''
def main_(url):
    # for i in range(start_,end_):

    optiona = ChromiumOptions().auto_port().incognito()
    tab_ = Chromium(optiona)
    tab_.clear_cache()
    tab_.cookies().clear()
    tab = tab_.latest_tab
    tab.get(url)

    time.sleep(4)

    # tab.ele('xpath://button[contains(@aria-label,"Accepter & Fermer")]').click()
    # time.sleep(2)
    # sr_ele2 = tab.ele('xpath://p[contains(text(), "//*[@id="find-broker"]/div/div[1]/form/div/div',timeout=30).shadow_root
    # sr_ele2 = tab.ele('xpath://form/div/div', timeout=30).shadow_root
    sr_ele2 = tab.ele('xpath://p[contains(text(), "Verify you are human")]/following-sibling::div/div/div', timeout=30).shadow_root
    iframe = sr_ele2.get_frame('xpath://iframe')
    second_shadow_root = iframe.ele("xpath://body").shadow_root
    # ele_ = second_shadow_root.ele("xpath://input[@type='checkbox']")
    # ele_1 = second_shadow_root.ele("xpath://span[contains(text(),'Vérifiez que vous êtes humain')]")
    ele_1 = second_shadow_root.ele("xpath://span[contains(text(),'Verify you are human')]")
    # space = Keys.TAB
    # body = tab.ele("tag:body")


    time.sleep(0.2)
    try:
        ele_1.click()
        # check_box = second_shadow_root.ele('xpath://input[@type="checkbox"]').click()
        # check_box.click()
    except Exception as e:
        print(e)
    time.sleep(5)
    html_data = tab.html
    tab_.quit()
    time.sleep(1)
    return html_data
    # time.sleep(3)
if __name__ == '__main__':
    # try:
    #     start_ = 1
    #     end_ = 5
    # except:
    #     start_ = sys.argv[1]
    #     end_ = sys.argv[2]
    main_(url)