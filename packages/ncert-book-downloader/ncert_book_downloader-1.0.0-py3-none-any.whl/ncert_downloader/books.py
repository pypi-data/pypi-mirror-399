"""
Complete list of all NCERT books with their download URLs.

This module contains the comprehensive catalog of NCERT textbooks
available for download, covering all classes from 1 to 12 in both
English and Hindi mediums.
"""

from ncert_downloader.models import Book


# Complete list of all NCERT books with their download URLs
NCERT_BOOKS: list[Book] = [
    # ==================== CLASS 12 ====================
    # Science Stream - English
    Book(12, "Physics", "Physics Part 1", "English", "https://ncert.nic.in/textbook/pdf/leph1dd.zip", 1),
    Book(12, "Physics", "Physics Part 2", "English", "https://ncert.nic.in/textbook/pdf/leph2dd.zip", 2),
    Book(12, "Chemistry", "Chemistry Part 1", "English", "https://ncert.nic.in/textbook/pdf/lech1dd.zip", 1),
    Book(12, "Chemistry", "Chemistry Part 2", "English", "https://ncert.nic.in/textbook/pdf/lech2dd.zip", 2),
    Book(12, "Maths", "Mathematics Part 1", "English", "https://ncert.nic.in/textbook/pdf/lemh1dd.zip", 1),
    Book(12, "Maths", "Mathematics Part 2", "English", "https://ncert.nic.in/textbook/pdf/lemh2dd.zip", 2),
    Book(12, "Biology", "Biology", "English", "https://ncert.nic.in/textbook/pdf/lebo1dd.zip"),
    
    # Science Stream - Hindi
    Book(12, "Physics", "भौतिकी भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhph1dd.zip", 1),
    Book(12, "Physics", "भौतिकी भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhph2dd.zip", 2),
    Book(12, "Chemistry", "रसायन विज्ञान भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhch1dd.zip", 1),
    Book(12, "Chemistry", "रसायन विज्ञान भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhch2dd.zip", 2),
    Book(12, "Maths", "गणित भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhmh1dd.zip", 1),
    Book(12, "Maths", "गणित भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhmh2dd.zip", 2),
    Book(12, "Biology", "जीवविज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/lhbo1dd.zip"),
    
    # Commerce Stream - English
    Book(12, "Accountancy", "Accountancy Part 1", "English", "https://ncert.nic.in/textbook/pdf/leac1dd.zip", 1),
    Book(12, "Accountancy", "Accountancy Part 2", "English", "https://ncert.nic.in/textbook/pdf/leac2dd.zip", 2),
    Book(12, "Business_Studies", "Business Studies Part 1", "English", "https://ncert.nic.in/textbook/pdf/lebs1dd.zip", 1),
    Book(12, "Business_Studies", "Business Studies Part 2", "English", "https://ncert.nic.in/textbook/pdf/lebs2dd.zip", 2),
    Book(12, "Economics", "Introductory Microeconomics", "English", "https://ncert.nic.in/textbook/pdf/leec2dd.zip", 1),
    Book(12, "Economics", "Introductory Macroeconomics", "English", "https://ncert.nic.in/textbook/pdf/leec1dd.zip", 2),
    
    # Commerce Stream - Hindi
    Book(12, "Accountancy", "लेखाशास्त्र भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhac1dd.zip", 1),
    Book(12, "Accountancy", "लेखाशास्त्र भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhac2dd.zip", 2),
    Book(12, "Business_Studies", "व्यवसाय अध्ययन भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhbs1dd.zip", 1),
    Book(12, "Business_Studies", "व्यवसाय अध्ययन भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhbs2dd.zip", 2),
    Book(12, "Economics", "व्यष्टि अर्थशास्त्र", "Hindi", "https://ncert.nic.in/textbook/pdf/lhec2dd.zip", 1),
    Book(12, "Economics", "सूक्ष्म अर्थशास्त्र", "Hindi", "https://ncert.nic.in/textbook/pdf/lhec1dd.zip", 2),
    
    # Arts Stream - English
    Book(12, "Geography", "Fundamental of Human Geography", "English", "https://ncert.nic.in/textbook/pdf/legy1dd.zip", 1),
    Book(12, "Geography", "India People and Economy", "English", "https://ncert.nic.in/textbook/pdf/legy2dd.zip", 2),
    Book(12, "Geography", "Practical Working Geography Part II", "English", "https://ncert.nic.in/textbook/pdf/legy3dd.zip", 3),
    Book(12, "History", "Themes in Indian History 1", "English", "https://ncert.nic.in/textbook/pdf/lehs1dd.zip", 1),
    Book(12, "History", "Themes in Indian History 2", "English", "https://ncert.nic.in/textbook/pdf/lehs2dd.zip", 2),
    Book(12, "History", "Themes in Indian History 3", "English", "https://ncert.nic.in/textbook/pdf/lehs3dd.zip", 3),
    Book(12, "Political_Science", "Contemporary World Politics", "English", "https://ncert.nic.in/textbook/pdf/leps1dd.zip", 1),
    Book(12, "Political_Science", "Politics in India since Independence", "English", "https://ncert.nic.in/textbook/pdf/leps2dd.zip", 2),
    Book(12, "Psychology", "Psychology", "English", "https://ncert.nic.in/textbook/pdf/lepy1dd.zip"),
    Book(12, "Sociology", "Indian Society", "English", "https://ncert.nic.in/textbook/pdf/lesy1dd.zip", 1),
    Book(12, "Sociology", "Social Change and Development India", "English", "https://ncert.nic.in/textbook/pdf/lesy2dd.zip", 2),
    
    # Arts Stream - Hindi
    Book(12, "Geography", "मानव भूगोल के मूल सिद्धांत", "Hindi", "https://ncert.nic.in/textbook/pdf/lhgy2dd.zip", 1),
    Book(12, "Geography", "भारत लोग और अर्थव्यवस्था", "Hindi", "https://ncert.nic.in/textbook/pdf/lhgy3dd.zip", 2),
    Book(12, "Geography", "भूगोल में प्रयोगात्मक कार्य", "Hindi", "https://ncert.nic.in/textbook/pdf/lhgy1dd.zip", 3),
    Book(12, "History", "भारतीय इतिहास के कुछ विषय भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/lhhs1dd.zip", 1),
    Book(12, "History", "भारतीय इतिहास के कुछ विषय भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhhs2dd.zip", 2),
    Book(12, "History", "भारतीय इतिहास के कुछ विषय भाग 3", "Hindi", "https://ncert.nic.in/textbook/pdf/lhhs3dd.zip", 3),
    Book(12, "Political_Science", "समकालीन विश्व राजनीति", "Hindi", "https://ncert.nic.in/textbook/pdf/lhps1dd.zip", 1),
    Book(12, "Political_Science", "स्वतंत्र भारत में राजनीति भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhps2dd.zip", 2),
    Book(12, "Psychology", "मनोविज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/lhpy1dd.zip"),
    Book(12, "Sociology", "भारतीय समाज", "Hindi", "https://ncert.nic.in/textbook/pdf/lhsy2dd.zip", 1),
    Book(12, "Sociology", "भारत में सामाजिक परिवर्तन और विकास", "Hindi", "https://ncert.nic.in/textbook/pdf/lhsy1dd.zip", 2),
    
    # Language Books - Class 12
    Book(12, "Hindi", "अंतरा", "Hindi", "https://ncert.nic.in/textbook/pdf/lhat1dd.zip", 1),
    Book(12, "Hindi", "अंतराल भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/lhan1dd.zip", 2),
    Book(12, "Hindi", "आरोह", "Hindi", "https://ncert.nic.in/textbook/pdf/lhar1dd.zip", 3),
    Book(12, "Hindi", "वितान", "Hindi", "https://ncert.nic.in/textbook/pdf/lhvt1dd.zip", 4),
    Book(12, "English", "Flamingo", "English", "https://ncert.nic.in/textbook/pdf/lefl1dd.zip", 1),
    Book(12, "English", "Kaleidoscope", "English", "https://ncert.nic.in/textbook/pdf/lekl1dd.zip", 2),
    Book(12, "English", "Vistas", "English", "https://ncert.nic.in/textbook/pdf/levt1dd.zip", 3),

    # ==================== CLASS 11 ====================
    # Science Stream - English
    Book(11, "Physics", "Physics Part 1", "English", "https://ncert.nic.in/textbook/pdf/keph1dd.zip", 1),
    Book(11, "Physics", "Physics Part 2", "English", "https://ncert.nic.in/textbook/pdf/keph2dd.zip", 2),
    Book(11, "Chemistry", "Chemistry Part 1", "English", "https://ncert.nic.in/textbook/pdf/kech1dd.zip", 1),
    Book(11, "Chemistry", "Chemistry Part 2", "English", "https://ncert.nic.in/textbook/pdf/kech2dd.zip", 2),
    Book(11, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/kemh1dd.zip"),
    Book(11, "Biology", "Biology", "English", "https://ncert.nic.in/textbook/pdf/kebo1dd.zip"),
    
    # Science Stream - Hindi
    Book(11, "Physics", "भौतिकी भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/khph1dd.zip", 1),
    Book(11, "Physics", "भौतिकी भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/khph2dd.zip", 2),
    Book(11, "Chemistry", "रसायन विज्ञान भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/khch1dd.zip", 1),
    Book(11, "Chemistry", "रसायन विज्ञान भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/khch2dd.zip", 2),
    Book(11, "Maths", "गणित", "Hindi", "https://ncert.nic.in/textbook/pdf/khmh1dd.zip"),
    Book(11, "Biology", "जीवविज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/khbo1dd.zip"),
    
    # Commerce Stream - English
    Book(11, "Accountancy", "Financial Accounting Part 1", "English", "https://ncert.nic.in/textbook/pdf/keac1dd.zip", 1),
    Book(11, "Accountancy", "Accountancy Part 2", "English", "https://ncert.nic.in/textbook/pdf/keac2dd.zip", 2),
    Book(11, "Business_Studies", "Business Studies", "English", "https://ncert.nic.in/textbook/pdf/kebs1dd.zip"),
    Book(11, "Economics", "Indian Economic Development", "English", "https://ncert.nic.in/textbook/pdf/keec1dd.zip"),
    
    # Commerce Stream - Hindi
    Book(11, "Accountancy", "लेखाशास्त्र भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/khac1dd.zip", 1),
    Book(11, "Accountancy", "लेखाशास्त्र भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/khac2dd.zip", 2),
    Book(11, "Business_Studies", "व्यवसाय अध्ययन", "Hindi", "https://ncert.nic.in/textbook/pdf/khbs1dd.zip"),
    Book(11, "Economics", "भारतीय अर्थव्यवस्था का विकास", "Hindi", "https://ncert.nic.in/textbook/pdf/khec1dd.zip"),
    
    # Arts Stream - English
    Book(11, "Geography", "Indian Physical Environment", "English", "https://ncert.nic.in/textbook/pdf/kegy1dd.zip", 1),
    Book(11, "Geography", "Fundamentals of Physical Geography", "English", "https://ncert.nic.in/textbook/pdf/kegy2dd.zip", 2),
    Book(11, "Geography", "Practical Work in Geography", "English", "https://ncert.nic.in/textbook/pdf/kegy3dd.zip", 3),
    Book(11, "History", "Themes in World History", "English", "https://ncert.nic.in/textbook/pdf/kehs1dd.zip"),
    Book(11, "Political_Science", "Indian Constitution at Work", "English", "https://ncert.nic.in/textbook/pdf/keps2dd.zip", 1),
    Book(11, "Political_Science", "Political Theory", "English", "https://ncert.nic.in/textbook/pdf/keps1dd.zip", 2),
    Book(11, "Psychology", "Introduction to Psychology", "English", "https://ncert.nic.in/textbook/pdf/kepy1dd.zip"),
    Book(11, "Sociology", "Introducing Sociology", "English", "https://ncert.nic.in/textbook/pdf/kesy1dd.zip", 1),
    Book(11, "Sociology", "Understanding Society", "English", "https://ncert.nic.in/textbook/pdf/kesy2dd.zip", 2),
    
    # Arts Stream - Hindi
    Book(11, "Geography", "भारतीय भौतिक पर्यावरण", "Hindi", "https://ncert.nic.in/textbook/pdf/khgy1dd.zip", 1),
    Book(11, "Geography", "भौतिक भूगोल के मूल सिद्धांत", "Hindi", "https://ncert.nic.in/textbook/pdf/khgy2dd.zip", 2),
    Book(11, "Geography", "भूगोल में प्रयोगात्मक कार्य भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/khgy3dd.zip", 3),
    Book(11, "History", "विश्व इतिहास के कुछ विषय", "Hindi", "https://ncert.nic.in/textbook/pdf/khhs1dd.zip"),
    Book(11, "Political_Science", "भारत का संविधान सिद्धांत और व्यवहार", "Hindi", "https://ncert.nic.in/textbook/pdf/khps2dd.zip", 1),
    Book(11, "Political_Science", "राजनीति सिद्धांत", "Hindi", "https://ncert.nic.in/textbook/pdf/khps1dd.zip", 2),
    Book(11, "Psychology", "मनोविज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/khpy1dd.zip"),
    Book(11, "Sociology", "समाजशास्त्र भाग 1", "Hindi", "https://ncert.nic.in/textbook/pdf/khsy1dd.zip", 1),
    Book(11, "Sociology", "समाज का बोध", "Hindi", "https://ncert.nic.in/textbook/pdf/khsy2dd.zip", 2),
    
    # Language Books - Class 11
    Book(11, "Hindi", "अंतरा", "Hindi", "https://ncert.nic.in/textbook/pdf/khat1dd.zip", 1),
    Book(11, "Hindi", "अंतराल", "Hindi", "https://ncert.nic.in/textbook/pdf/khan1dd.zip", 2),
    Book(11, "Hindi", "आरोह", "Hindi", "https://ncert.nic.in/textbook/pdf/khar1dd.zip", 3),
    Book(11, "Hindi", "वितान", "Hindi", "https://ncert.nic.in/textbook/pdf/khvt1dd.zip", 4),
    Book(11, "English", "Hornbill", "English", "https://ncert.nic.in/textbook/pdf/kehb1dd.zip", 1),
    Book(11, "English", "Snapshots Supplementary Reader", "English", "https://ncert.nic.in/textbook/pdf/kesp1dd.zip", 2),
    Book(11, "English", "Woven Words", "English", "https://ncert.nic.in/textbook/pdf/keww1dd.zip", 3),

    # ==================== CLASS 10 ====================
    Book(10, "Science", "Science", "English", "https://ncert.nic.in/textbook/pdf/jesc1dd.zip"),
    Book(10, "Science", "विज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/jhsc1dd.zip"),
    Book(10, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/jemh1dd.zip"),
    Book(10, "Maths", "गणित", "Hindi", "https://ncert.nic.in/textbook/pdf/jhmh1dd.zip"),
    Book(10, "Social_Science", "Contemporary India", "English", "https://ncert.nic.in/textbook/pdf/jess1dd.zip", 1),
    Book(10, "Social_Science", "India and the Contemporary World-II", "English", "https://ncert.nic.in/textbook/pdf/jess3dd.zip", 2),
    Book(10, "Social_Science", "Understanding Economic Development", "English", "https://ncert.nic.in/textbook/pdf/jess2dd.zip", 3),
    Book(10, "Social_Science", "Democratic Politics-II", "English", "https://ncert.nic.in/textbook/pdf/jess4dd.zip", 4),
    Book(10, "Social_Science", "भारत और समकालीन विश्व भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/jhss3dd.zip", 1),
    Book(10, "Social_Science", "आर्थिक विकास की समझ", "Hindi", "https://ncert.nic.in/textbook/pdf/jhss2dd.zip", 2),
    Book(10, "Social_Science", "समकालीन भारत", "Hindi", "https://ncert.nic.in/textbook/pdf/jhss1dd.zip", 3),
    Book(10, "Social_Science", "लोकतान्त्रिक राजनीति", "Hindi", "https://ncert.nic.in/textbook/pdf/jhss4dd.zip", 4),
    Book(10, "Hindi", "कृतिका", "Hindi", "https://ncert.nic.in/textbook/pdf/jhkr1dd.zip", 1),
    Book(10, "Hindi", "क्षितिज", "Hindi", "https://ncert.nic.in/textbook/pdf/jhks1dd.zip", 2),
    Book(10, "Hindi", "संचयन भाग 2", "Hindi", "https://ncert.nic.in/textbook/pdf/jhsy1dd.zip", 3),
    Book(10, "Hindi", "स्पर्श", "Hindi", "https://ncert.nic.in/textbook/pdf/jhsp1dd.zip", 4),
    Book(10, "English", "First Flight", "English", "https://ncert.nic.in/textbook/pdf/jeff1dd.zip", 1),
    Book(10, "English", "Footprints Without Feet", "English", "https://ncert.nic.in/textbook/pdf/jefp1dd.zip", 2),

    # ==================== CLASS 9 ====================
    Book(9, "Science", "Science", "English", "https://ncert.nic.in/textbook/pdf/iesc1dd.zip"),
    Book(9, "Science", "विज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/ihsc1dd.zip"),
    Book(9, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/iemh1dd.zip"),
    Book(9, "Maths", "गणित", "Hindi", "https://ncert.nic.in/textbook/pdf/ihmh1dd.zip"),
    Book(9, "Social_Science", "Contemporary India", "English", "https://ncert.nic.in/textbook/pdf/iess1dd.zip", 1),
    Book(9, "Social_Science", "India and the Contemporary World-I", "English", "https://ncert.nic.in/textbook/pdf/iess3dd.zip", 2),
    Book(9, "Social_Science", "Economics", "English", "https://ncert.nic.in/textbook/pdf/iess2dd.zip", 3),
    Book(9, "Social_Science", "Democratic Politics", "English", "https://ncert.nic.in/textbook/pdf/iess4dd.zip", 4),
    Book(9, "Social_Science", "भारत और समकालीन विश्व भाग I", "Hindi", "https://ncert.nic.in/textbook/pdf/ihss3dd.zip", 1),
    Book(9, "Social_Science", "अर्थशास्त्र", "Hindi", "https://ncert.nic.in/textbook/pdf/ihss2dd.zip", 2),
    Book(9, "Social_Science", "समकालीन भारत", "Hindi", "https://ncert.nic.in/textbook/pdf/ihss1dd.zip", 3),
    Book(9, "Social_Science", "लोकतान्त्रिक राजनीति", "Hindi", "https://ncert.nic.in/textbook/pdf/ihss4dd.zip", 4),
    Book(9, "Hindi", "कृतिका", "Hindi", "https://ncert.nic.in/textbook/pdf/ihkr1dd.zip", 1),
    Book(9, "Hindi", "क्षितिज", "Hindi", "https://ncert.nic.in/textbook/pdf/ihks1dd.zip", 2),
    Book(9, "Hindi", "संचयन", "Hindi", "https://ncert.nic.in/textbook/pdf/ihsa1dd.zip", 3),
    Book(9, "Hindi", "स्पर्श", "Hindi", "https://ncert.nic.in/textbook/pdf/ihsp1dd.zip", 4),
    Book(9, "English", "Beehive", "English", "https://ncert.nic.in/textbook/pdf/iebe1dd.zip", 1),
    Book(9, "English", "Moments Supplementary Reader", "English", "https://ncert.nic.in/textbook/pdf/iemo1dd.zip", 2),
    Book(9, "English", "Words and Expressions", "English", "https://ncert.nic.in/textbook/pdf/iewe1dd.zip", 3),

    # ==================== CLASS 8 ====================
    Book(8, "Science", "Science", "English", "https://ncert.nic.in/textbook/pdf/hesc1dd.zip"),
    Book(8, "Science", "विज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/hhsc1dd.zip"),
    Book(8, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/hemh1dd.zip"),
    Book(8, "Maths", "गणित", "Hindi", "https://ncert.nic.in/textbook/pdf/hhmh1dd.zip"),
    Book(8, "Social_Science", "Exploring Society: India and Beyond", "English", "https://ncert.nic.in/textbook/pdf/hees1dd.zip", 1),
    Book(8, "Social_Science", "Our Past-III Part 2", "English", "https://ncert.nic.in/textbook/pdf/hess2dd.zip", 2),
    Book(8, "Social_Science", "Social and Political Life", "English", "https://ncert.nic.in/textbook/pdf/hess3dd.zip", 3),
    Book(8, "Social_Science", "Resource and Development", "English", "https://ncert.nic.in/textbook/pdf/hess4dd.zip", 4),
    Book(8, "Social_Science", "Hamare Atit III", "Hindi", "https://ncert.nic.in/textbook/pdf/hhss1dd.zip", 1),
    Book(8, "Social_Science", "Hamare Atit Part 2", "Hindi", "https://ncert.nic.in/textbook/pdf/hhss2dd.zip", 2),
    Book(8, "Social_Science", "Samajik Evam Rajnitik Jeevan", "Hindi", "https://ncert.nic.in/textbook/pdf/hhss3dd.zip", 3),
    Book(8, "Social_Science", "Sansadhan Evam Vikas", "Hindi", "https://ncert.nic.in/textbook/pdf/hhss4dd.zip", 4),
    Book(8, "Hindi", "भारत की खोज", "Hindi", "https://ncert.nic.in/textbook/pdf/hhbk1dd.zip", 1),
    Book(8, "Hindi", "दूर्वा", "Hindi", "https://ncert.nic.in/textbook/pdf/hhdv1dd.zip", 2),
    Book(8, "Hindi", "वसंत", "Hindi", "https://ncert.nic.in/textbook/pdf/hhvs1dd.zip", 3),
    Book(8, "English", "Honeydew", "English", "https://ncert.nic.in/textbook/pdf/hehd1dd.zip", 1),
    Book(8, "English", "It So Happened", "English", "https://ncert.nic.in/textbook/pdf/heih1dd.zip", 2),

    # ==================== CLASS 7 ====================
    Book(7, "Science", "Science", "English", "https://ncert.nic.in/textbook/pdf/gesc1dd.zip"),
    Book(7, "Science", "विज्ञान", "Hindi", "https://ncert.nic.in/textbook/pdf/ghsc1dd.zip"),
    Book(7, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/gemh1dd.zip"),
    Book(7, "Maths", "गणित", "Hindi", "https://ncert.nic.in/textbook/pdf/ghmh1dd.zip"),
    Book(7, "Social_Science", "Exploring Society: India and Beyond", "English", "https://ncert.nic.in/textbook/pdf/gees1dd.zip", 1),
    Book(7, "Social_Science", "Social and Political Life-II", "English", "https://ncert.nic.in/textbook/pdf/gess3dd.zip", 2),
    Book(7, "Social_Science", "Our Environment", "English", "https://ncert.nic.in/textbook/pdf/gess2dd.zip", 3),
    Book(7, "Social_Science", "Hamare Atit II", "Hindi", "https://ncert.nic.in/textbook/pdf/ghss1dd.zip", 1),
    Book(7, "Social_Science", "Hamara Paryavaran", "Hindi", "https://ncert.nic.in/textbook/pdf/ghss2dd.zip", 2),
    Book(7, "Social_Science", "Samajik Vigyan", "Hindi", "https://ncert.nic.in/textbook/pdf/ghes1dd.zip", 3),
    Book(7, "Hindi", "दूर्वा", "Hindi", "https://ncert.nic.in/textbook/pdf/ghdv1dd.zip", 1),
    Book(7, "Hindi", "महाभारत", "Hindi", "https://ncert.nic.in/textbook/pdf/ghmb1dd.zip", 2),
    Book(7, "Hindi", "वसंत", "Hindi", "https://ncert.nic.in/textbook/pdf/ghvs1dd.zip", 3),
    Book(7, "English", "Honeycomb", "English", "https://ncert.nic.in/textbook/pdf/gehc1dd.zip", 1),
    Book(7, "English", "An Alien Hand Supplementary Reader", "English", "https://ncert.nic.in/textbook/pdf/geah1dd.zip", 2),

    # ==================== CLASS 6 ====================
    # Science
    Book(6, "Science", "Science", "English", "https://ncert.nic.in/textbook/pdf/fecu1dd.zip"),
    Book(6, "Science", "Curiosity (Science)", "Hindi", "https://ncert.nic.in/textbook/pdf/fhcu1dd.zip"),
    
    # Maths
    Book(6, "Maths", "Mathematics", "English", "https://ncert.nic.in/textbook/pdf/fegp1dd.zip"),
    Book(6, "Maths", "Ganit", "Hindi", "https://ncert.nic.in/textbook/pdf/fhgp1dd.zip"),
    
    # Social Science
    Book(6, "Social_Science", "Exploring Society: India and Beyond", "English", "https://ncert.nic.in/textbook/pdf/fees1dd.zip"),
    Book(6, "Social_Science", "Samajik Vigyan", "Hindi", "https://ncert.nic.in/textbook/pdf/fhes1dd.zip"),
    
    # Languages
    Book(6, "Hindi", "Malhar", "Hindi", "https://ncert.nic.in/textbook/pdf/fhml1dd.zip"),
    Book(6, "English", "Poorvi", "English", "https://ncert.nic.in/textbook/pdf/fepr1dd.zip"),

    # ==================== CLASS 5 ====================
    Book(5, "Maths", "Math Magic", "English", "https://ncert.nic.in/textbook/pdf/eemh1dd.zip"),
    Book(5, "Maths", "गणित का जादू", "Hindi", "https://ncert.nic.in/textbook/pdf/ehmh1dd.zip"),
    Book(5, "EVS", "Looking Around", "English", "https://ncert.nic.in/textbook/pdf/eeap1dd.zip"),
    Book(5, "EVS", "आस पास", "Hindi", "https://ncert.nic.in/textbook/pdf/ehap1dd.zip"),
    Book(5, "Hindi", "रिमझिम", "Hindi", "https://ncert.nic.in/textbook/pdf/ehhn1dd.zip"),
    Book(5, "English", "Marigold", "English", "https://ncert.nic.in/textbook/pdf/eeen1dd.zip"),

    # ==================== CLASS 4 ====================
    Book(4, "Hindi", "Veena", "Hindi", "https://ncert.nic.in/textbook/pdf/dhve1dd.zip"),
    Book(4, "English", "Santoor", "English", "https://ncert.nic.in/textbook/pdf/desa1dd.zip"),
    Book(4, "Maths", "Math Mela", "English", "https://ncert.nic.in/textbook/pdf/demm1dd.zip"),
    Book(4, "Maths", "Ganit Mela", "Hindi", "https://ncert.nic.in/textbook/pdf/dhmm1dd.zip"),

    # ==================== CLASS 3 ====================
    Book(3, "Maths", "Math Mela", "English", "https://ncert.nic.in/textbook/pdf/cemm1dd.zip"),
    Book(3, "Maths", "Ganit Mala", "Hindi", "https://ncert.nic.in/textbook/pdf/chmm1dd.zip"),
    Book(3, "English", "Santoor", "English", "https://ncert.nic.in/textbook/pdf/cesa1dd.zip"),
    Book(3, "EVS", "Our Wondrous World", "English", "https://ncert.nic.in/textbook/pdf/ceww1dd.zip"),
    Book(3, "PE", "Khel Yoga", "Hindi", "https://ncert.nic.in/textbook/pdf/ceky1dd.zip"),
    Book(3, "Hindi", "Veena", "Hindi", "https://ncert.nic.in/textbook/pdf/chve1dd.zip"),

    # ==================== CLASS 2 ====================
    Book(2, "Maths", "Joyful Mathematics", "English", "https://ncert.nic.in/textbook/pdf/bejm1dd.zip"),
    Book(2, "Maths", "Aanandmay Ganit", "Hindi", "https://ncert.nic.in/textbook/pdf/bhjm1dd.zip"),
    Book(2, "Hindi", "Sarangi", "Hindi", "https://ncert.nic.in/textbook/pdf/bhsr1dd.zip"),
    Book(2, "English", "Mridang", "English", "https://ncert.nic.in/textbook/pdf/bemr1dd.zip"),

    # ==================== CLASS 1 ====================
    Book(1, "English", "Mridang", "English", "https://ncert.nic.in/textbook/pdf/aemr1dd.zip"),
    Book(1, "Maths", "Joyful Mathematics", "English", "https://ncert.nic.in/textbook/pdf/aejm1dd.zip"),
    Book(1, "Maths", "Aanandmay Ganit", "Hindi", "https://ncert.nic.in/textbook/pdf/ahjm1dd.zip"),
    Book(1, "Hindi", "Sarangi", "Hindi", "https://ncert.nic.in/textbook/pdf/ahsr1dd.zip"),
]


def get_books_by_class(class_num: int) -> list[Book]:
    """Get all books for a specific class."""
    return [b for b in NCERT_BOOKS if b.class_num == class_num]


def get_books_by_subject(subject: str) -> list[Book]:
    """Get all books for a specific subject (case-insensitive)."""
    return [b for b in NCERT_BOOKS if b.subject.lower() == subject.lower()]


def get_books_by_language(language: str) -> list[Book]:
    """Get all books for a specific language."""
    return [b for b in NCERT_BOOKS if b.language.lower() == language.lower()]


def get_total_books_count() -> int:
    """Get the total number of books in the catalog."""
    return len(NCERT_BOOKS)
