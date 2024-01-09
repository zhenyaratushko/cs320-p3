# project: p3
# submitter: ratushko
# partner: none
# hours: 13

import pandas as pd
import requests
import time
from collections import deque
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class Parent:
    def twice(self):
        self.message()
        self.message()
        
    def message(self):
        print("parent says hi")
        
class Child(Parent):
    def message(self):
        print("child says hi")
        
c = Child()

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def visit_and_get_children(self, node):
        """ Record the node value in self.order, and return its children
        param: node
        return: children of the given node
        """
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        self.visited.clear()
        self.order.clear()
        self.dfs_visit(node)

    def dfs_visit(self, node):
        if node in self.visited:
            return
        self.visited.add(node)
        children = self.visit_and_get_children(node)
        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self, node):
        queue = deque([node])
        visited = {node}
        
        while len(queue) > 0:
            curr_node = queue.popleft()

            for child in self.visit_and_get_children(curr_node):
                if child not in visited:
                    queue.append(child)
                    visited.add(child)

class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__()
        self.df = df

    def visit_and_get_children(self, node):
        self.order.append(node)
        children = []
        for label, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(label)
        return children
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        self.directory = "file_nodes"
        
    def visit_and_get_children(self, file):
        with open(f"{self.directory}/{file}") as f:
            lines = f.readlines()
        
        children = []
        new_lines = []
        
        for line in lines:
            new_lines.append(line.replace("\n", ""))

        self.order.append(new_lines[0])
        children.extend(new_lines[1].split(","))
            
        return children
    
    def concat_order(self):
        concatenated_string = ""
        
        for value in self.order:
            concatenated_string += value
        
        return concatenated_string
    
class WebSearcher(GraphSearcher):    
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.content = []
        
    def visit_and_get_children(self, node):
        self.order.append(node)
        self.driver.get(node)
        self.content.append(pd.read_html(node)[0])
        
        children = []
        
        for element in self.driver.find_elements("tag name", "a"):
            children.append(element.get_attribute("href"))
        
        return children
                            
    def table(self):
        table = pd.concat(self.content, ignore_index=True)
        return table

def reveal_secrets(driver, url, travellog):
    password = ""
    for item in travellog['clue']:
        password += str(item)

    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(20) 

    text = driver.find_element("id", "password")
    text.send_keys(password)
    button = driver.find_element("id", "attempt-button")
    button.click()
    time.sleep(1)
    
    loc_button = driver.find_element("id", "locationBtn")
    loc_button.click()
    time.sleep(1)
    
    jpg = driver.find_element("id", "image").get_attribute("src")
    jpg_req = requests.get(jpg)
    with open("Current_Location.jpg", "wb") as binary_file: #taken from https://www.geeksforgeeks.org/python-write-bytes-to-file/
        binary_file.write(jpg_req.content)
        
    hidden_location = driver.find_element("id", "location").text
    return hidden_location    