from selenium import webdriver
import unittest
import time, datetime

class Tellurium(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:7003/"
        self.verificationErrors = []
        self.accept_next_alert = True
        

    def login_helper(self):
        driver = self.driver
        
        driver.get(self.base_url + "list/")
        login = driver.find_element_by_link_text('login')
        login.click()
        
        driver.find_element_by_id('admin').click()
        driver.find_element_by_id('submit-login').click()
    
    
    def test_sequence(self):
        driver = self.driver
        self.login_helper() 

        driver.get(self.base_url + "edit/")
        driver.execute_script("CKEDITOR.instances.id_content.setData('stuff');");
        driver.find_element_by_id('id_title').send_keys('delete me')
        driver.find_element_by_id('id_tags').send_keys('some,tags')

        pub = driver.find_element_by_id('id_published_at').get_attribute('value')
        dt = datetime.datetime.strptime(pub, '%Y-%m-%d %H:%M:%S' )
        
        driver.find_element_by_id("btn_save_continue").click()
        self.assertEqual(driver.current_url,'http://localhost:7003/edit/delete-me/')

        self.assertEqual(pub, driver.find_element_by_id('id_published_at').get_attribute('value'))
        
        driver.find_element_by_class_name('btn-danger').click()
        driver.find_element_by_class_name('btn-danger').click()
        
        driver.quit()
        
    def test_timestamp(self):
        driver = self.driver
        self.login_helper()

        self.assertEqual('http://localhost:7003/list/', driver.current_url)
        
        driver.get(self.base_url + "edit/")
        time.sleep(1)
        
        t = time.time()

        pub = driver.find_element_by_id('id_published_at').get_attribute('value')
        dt = datetime.datetime.strptime(pub, '%Y-%m-%d %H:%M:%S' )
        self.assertGreater(driver.find_element_by_id('id_timestamp').get_attribute('value'),t)
        self.assertNotEqual(pub, '')
        
        driver.find_element_by_id("btn_save_continue").click()
        self.assertEqual(driver.find_element_by_id('id_published_at').get_attribute('value'), pub)
        self.assertEqual(int(time.mktime(dt.utctimetuple())*1000),
                         int(driver.find_element_by_id('id_timestamp').get_attribute('value')) )
        
        driver.quit()
        
if __name__ == "__main__":
    unittest.main()
