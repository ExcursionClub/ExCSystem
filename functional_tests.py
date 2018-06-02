from selenium import webdriver

browser = webdriver.Firefox()
browser.get('http://localhost:8000/kiosk')

assert 'Kiosk' in browser.title
