from flask import Flask, request, render_template, jsonify
from bs4 import BeautifulSoup as bs
import requests
from urllib.request import urlopen
import logging
from pymongo.mongo_client import MongoClient
logging.basicConfig(filename = "flipkart_review_scrapper_flask.log", level = logging.INFO, filemode='w',format='%(asctime)s %(process)d %(levelname)s %(message)s')
#logging filemode='w' will earse everthing inside then start loging

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template("index.html")
    #return "<h1>Hello, World!</h1>"


@app.route("/result", methods=['GET','POST'])
def result_review_func():
    if(request.method == 'POST'):
        try:

            search_string = request.form['search_p'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + search_string
            url_client = urlopen(flipkart_url)
            flipkart_page = url_client.read()
            url_client.close()

            flipkart_html = bs(flipkart_page, "html.parser")
            products_boxes = flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})

            del products_boxes[0:3]

            product_1 = products_boxes[0]
            product_link = "https://www.flipkart.com" + product_1.div.div.div.a['href']

            #product_page = requests.get(products_link)
            product_response = requests.get(product_link)
            #return product_response.text

            product_html = bs(product_response.text, 'html.parser')
            #print(product_html)
            
            product_comment_boxes = product_html.find_all("div",{"class":"_16PBlm"})
            #print(product_comment_boxes)
            print(len(product_comment_boxes))

            file_name = search_string + ".csv"
            fw = open(file_name, 'w')
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)

            reviews = []
            #print(reviews)
            for comment_box in product_comment_boxes:
                try:
                    name = comment_box.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                    #print(name)
                except:
                    logging.info("name")

                try:
                    rating = comment_box.div.div.div.div.text
                    #print(rating)
                except:
                    rating = "No Rating"
                    logging.info("rating")

                try:
                    comment_head = comment_box.div.div.div.p.text
                    #print(comment_head)
                except:
                    comment_head = "No Heading"
                    logging.info("heading")

                try:
                    #comment = comment_box.div.div.find_all("div",{"class":""})[0].text
                    comment_tag = comment_box.div.div.find_all("div",{"class":""})
                    cust_comment = comment_tag[0].text
                    #print(cust_comment)
                except Exception as e:
                    #logging.info("comment",e) #this won't print on log file
                    logging.info(f"comment{e}") #can't write "string" inside log, otherwise will terminate program
                    

                mydict = {"product":search_string, "name":name, "rating":rating, "heading":comment_head,
                         "comment":cust_comment }
                #print("dhflfd")
                reviews.append(mydict)
                #print(reviews)

            #print(reviews)

            logging.info("logging my final result {}".format(reviews)) #print result on log file
            
            #fw.write(reviews) #print dataset on created .csv file
            fw.write(str(reviews)) # file write() only let str type to print
            fw.close()
            

            uri = "mongodb+srv://pwskills:pwskills1@cluster0.xe9xplu.mongodb.net/?retryWrites=true&w=majority"
            # Create a new client and connect to the server
            client = MongoClient(uri)
            # Send a ping to confirm a successful connection
            db = client['flip_rev_scrap']
            coll_flipkart_1 = db['flipkt_product_review']
            coll_flipkart_1.insert_many(reviews)
            #coll_flipkart_1.drop()

            #return "<h1>Hello, World!</h1>"
            #return render_template("result.html")
            #return render_template("result.html",reviews) # render_template() can't pass dataset like this
            return render_template("result.html",reviews=reviews[0:(len(reviews)-1)])            
            #return render_template("result.html",reviews=reviews) #this will work but it's printing extra same review comment
        
        except Exception as e:
            logging.info(e)
            return "something is wrong"
    
    else:
        logging.info("error in checking if POST method",e)
        return render_template("index.html")


if __name__=="__main__":
    app.run(host="0.0.0.0")
