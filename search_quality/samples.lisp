(defparameter *moscow-viewport*
  (viewport :maxx 38.0314 :maxy 67.7348 :minx 37.1336 :miny 67.1349))
(defparameter *moscow-position*
  (position-lat-lon 55.751633 37.618705))

(defparameter *minsk-viewport*
  (viewport :maxx 27.5653 :maxy 64.2473 :minx 27.5585 :miny 64.242))
(defparameter *minsk-position*
  (position-lat-lon 53.9023339 27.5618798))

(defparameter *hrodna-viewport*
  (viewport :maxx 23.841444 :maxy 63.879684 :minx 23.8265894 :miny 63.869197))
(defparameter *hrodna-position*
  (position-lat-lon 53.6834584 23.8342624))

(defparameter *skylight-viewport*
  (viewport :maxx 37.5409 :maxy 67.538 :minx 37.533 :miny 67.533))
(defparameter *skylight-position*
  (position-lat-lon 55.7967341 37.5373559))

(defparameter *moscow-airport-station-viewport*
  (viewport :maxx 37.5367 :maxy 67.5442 :minx 37.5316 :miny 67.539))
(defparameter *moscow-airport-station-position*
  (position-lat-lon 55.799996 37.5343679))

(defparameter *zelenograd-viewport*
  (viewport :maxx 37.2032 :maxy 67.8953 :minx 37.1945 :miny 67.8886))
(defparameter *zelenograd-position*
  (position-lat-lon 55.9964055 37.1984455))

(dolist (query '("жуковский" "жуковский "))
  (defsample query "ru"
    (position-lat-lon 55.82483 37.566872)
    (viewport :maxx 37.5704 :maxy 67.5886 :minx 37.5633 :miny 67.5831)
    (list (vital "Жуковский" '("place-city") (position-lat-lon 55.597279 38.119967)))))

(defsample "варшава " "ru"
  (position-lat-lon 55.82483 37.566872)
  (viewport :maxx 37.5704 :maxy 67.5886 :minx 37.5633 :miny 67.5831)
  (list (vital "Warszawa" '("place-city-capital-2") (position-lat-lon 52.231918 21.006742))))

(defsample "первомайск " "ru"
  (position-lat-lon 55.82483 37.566872)
  (viewport :maxx 37.5704 :maxy 67.5886 :minx 37.5633 :miny 67.5831)
  (list (vital "Первомайск" '("place-town") (position-lat-lon 54.865758 43.805049))))

(defsample "бежецк" "ru"
  (position-lat-lon 55.662164 37.63057)
  (viewport :maxx 37.6341 :maxy 67.2996 :minx 37.627 :miny 67.2941)
  (list (vital "Бежецк" '("place-town") (position-lat-lon 57.781353 36.692516))))

(defsample "бутово" "ru"
  (position-lat-lon 55.662164 37.63057)
  (viewport :maxx 37.6341 :maxy 67.2996 :minx 37.627 :miny 67.2941)
  (list (vital "Бутово" '("place-hamlet") (position-lat-lon 55.5428188 37.5854318))))

(dolist (query '("старо" "старок"))
  (defsample query "ru"
    (position-lat-lon 55.662164 37.63057)
    (viewport :maxx 37.6341 :maxy 67.2996 :minx 37.627 :miny 67.2941)
    (list (relevant "Старокаширское шоссе"
                    '("hwtag-lit" "hwtag-oneway" "highway-residential")
                    (position-lat-lon 55.661427 37.6305476)))))

(defsample "ленинск" "ru"
  (position-lat-lon 55.662164 37.63057)
  (viewport :maxx 37.6341 :maxy 67.2996 :minx 37.627 :miny 67.2941)
  (list (relevant "Ленинский проспект"
                  '("hwtag-nofoot" "hwtag-oneway" "highway-primary")
                  (position-lat-lon 55.6974076 37.5626246))))
(defsample "героев панфиловцев 22" "ru"
  (position-lat-lon 55.662164 37.63057)
  (viewport :maxx 37.6341 :maxy 67.2996 :minx 37.627 :miny 67.2941)
  (list (vital "" '("building")
               (position-lat-lon 55.856544 37.410764)
               :house-number "22")))

(defsample "АЗС" "ru"
  (position-lat-lon 55.658 37.6403)
  (viewport :maxx 37.6438 :maxy 67.2923 :minx 37.6367 :miny 67.2868)
  (list (relevant "Eka" '("amenity-fuel")
                  (position-lat-lon 55.658089 37.640331))))

(defsample "Шереметьево" "ru"
  (position-lat-lon 55.658 37.6403)
  (viewport :maxx 37.6438 :maxy 67.2923 :minx 37.6367 :miny 67.2868)
  (list (vital "Международный аэропорт Шереметьево"
               '("aeroway-aerodrome-international")
               (position-lat-lon 55.972948 37.412647))))

(defsample "kamyshin volga river" "en"
  (position-lat-lon 50.0523 45.44)
  (viewport :maxx 45.6714 :maxy 58.2199 :minx 45.2917 :miny 57.9277)
  (list (relevant "Волга"
                  '("waterway-river" "boundary-administrative-6" "boundary-administrative-8")
                  (position-lat-lon 50.052265 45.439982))
        (relevant "Волга"
                  '("waterway-river" "boundary-administrative-6" "boundary-administrative-8")
                  (position-lat-lon 50.098178 45.485677))))

(defsample "москва балчуг 7" "ru"
  (position-lat-lon 55.74489 37.627992)
  (viewport :maxx 37.6316 :maxy 67.4464 :minx 37.6244 :miny 67.4409)
  (list (vital "" '("building") (position-lat-lon 55.746825 37.626597)
               :house-number "7")))

(defsample "train station подольск" "en"
  (position-lat-lon 54.192024 37.615781)
  (viewport :maxx 37.6184 :maxy 64.745 :minx 37.607 :miny 64.7345)
  (list (vital "Подольск" '("railway-station")
               (position-lat-lon 55.431798 37.565417))))

(defsample "Байкал" "en"
  (position-lat-lon 55.751624 37.618715)
  (viewport :maxx 37.6215 :maxy 67.4589 :minx 37.616 :miny 67.4525)
  (cons (relevant "Озеро \"Байкал\"" '("natural-water")
                  (position-lat-lon 53.737727 108.290227))
        (loop for (lat lon) in '((53.027245 106.74882)
                                 (53.518324 107.535302)
                                 (53.500603 108.29637))
           collecting (relevant "озеро Байкал" '("natural-water")
                                (position-lat-lon lat lon)))))

(defsample "памятник высоцкому" "ru"
  *moscow-position*
  *moscow-viewport*
  (list (vital "Памятник В.С. Высоцкому" '("historic-memorial")
               (position-lat-lon 55.768153 37.613128))))

(defsample "san francisco golden gate " "en"
  (position-lat-lon 37.806395 -122.475599)
  (viewport :maxx -122.445 :maxy 40.924 :minx -122.505 :miny 40.8735)
  (list (relevant "Golden Gate Bridge" '("tourism-attraction")
                  (position-lat-lon 37.8222 -122.478874))))

(defsample "810 7th street northwest washington" "en"
  (position-lat-lon 38.900353 -77.022134)
  (viewport :maxx -77.0202 :maxy 42.2884 :minx -77.024 :miny 42.2853)
  (list (vital "RFD" '("amenity-pub")
               (position-lat-lon 38.900353 -77.022134)
               :house-number "810")))

(defsample "немига" "ru"
  (position-lat-lon 53.902333 27.56189)
  (viewport :maxx 27.7138 :maxy 64.39 :minx 27.2672 :miny 64.0178)
  (list (relevant "улица Немига" '("hwtag-oneway" "highway-primary")
                  (position-lat-lon 53.9058845 27.5547772))
        (relevant "улица Немига" '("hwtag-oneway" "highway-primary_link")
                  (position-lat-lon 53.9018527 27.5485398))
        (relevant "Немига" '("railway-subway_entrance-minsk")
                  (position-lat-lon 53.906155 27.553509))))

(defsample "купавна " "ru"
  *moscow-position*
  (viewport :maxx 37.6253 :maxy 67.4611 :minx 37.6121 :miny 67.4502)
  (list (relevant "Старая Купавна" '("place-town")
                  (position-lat-lon 55.807038 38.17743))
        (relevant "Купавна" '("place-village")
                  (position-lat-lon 55.748353 38.122308))))

(defsample "купавна малая московская" "ru"
  *moscow-position*
  (viewport :maxx 37.6253 :maxy 67.4611 :minx 37.6121 :miny 67.4502)
  (list (relevant "Малая Московская улица" '("highway-secondary")
                  (position-lat-lon 55.805866 38.151669))))

(defsample "riga" "en"
  (position-lat-lon 55.593326 37.653758)
  (viewport :maxx 37.7799 :maxy 67.304 :minx 37.5064 :miny 67.0476)
  (list (vital "Rīga" '("place-city-capital-2")
               (position-lat-lon 56.949391 24.105187))))

(defsample "ленинградский проспект 75" "en"
  (position-lat-lon 55.804683 37.511168)
  (viewport :maxx 37.5145 :maxy 67.552 :minx 37.5094 :miny 67.5472)
  (loop for (house-number lat lon) in '(("75 к1" 55.804945 37.512323)
                                        ("75 к1А" 55.804198 37.513327)
                                        ("75 к1Б" 55.804729 37.510496)
                                        ("75 с2" 55.804332 37.511761)
                                        ("75А" 55.803425 37.512232)
                                        ("75Б" 55.804002 37.511482))
     collecting (relevant "" '("building") (position-lat-lon lat lon)
                          :house-number house-number)))

(defsample "минск немига 3" "ru"
  (position-lat-lon 53.893297 27.567588)
  (viewport :maxx 27.5728 :maxy 64.2351 :minx 27.561 :miny 64.2241)
  (list (vital "Немига" '("building" "shop-mall")
               (position-lat-lon 53.904068 27.552464)
               :house-number "3")))

(defsample "улица наметкина 16 " "en"
  *moscow-position*
  *moscow-viewport*
  (list (vital "Газпром" '("building")
               (position-lat-lon 55.658734 37.55672)
               :house-number "16")
        (relevant "Газпромбанк" '("building" "amenity-bank")
                  (position-lat-lon 55.659377 37.558571)
                  :house-number "16 к1")
        (relevant "Gazprom" '("building")
                  (position-lat-lon 55.65896 37.557985)
                  :house-number "16 к2")
        (relevant "" '("building")
                  (position-lat-lon 55.658486 37.55745)
                  :house-number "16 к3")
        (relevant "Поликлиника и физкультурно-оздоровительный корпус"
                  '("building" "amenity-clinic")
                  (position-lat-lon 55.658012 37.556947)
                  :house-number "16 к4")
        (relevant "" '("building")
                  (position-lat-lon 55.658722 37.55582)
                  :house-number "16 к7")
        (relevant "" '("building")
                  (position-lat-lon 55.658219 37.555958)
                  :house-number "16 к5")
        (relevant "Газпром-отель" '("building" "tourism-hotel")
                  (position-lat-lon 55.658549 37.555085)
                  :house-number "16 к6")))

(defsample "cuba" "en"
  *moscow-position*
  *moscow-viewport*
  (list (relevant "Cuba" '("place-country")
                  (position-lat-lon 23.013134 -80.832884))))

(defsample "540 queen street brisbane" "en"
  (position-lat-lon -27.469546 153.024131)
  (viewport :maxx 153.027 :maxy -28.5833 :minx 153.02 :miny -28.5888)
  (list (vital "Willahra Tower" '("building")
               (position-lat-lon -27.463288 153.030955)
               :house-number "540")))

(defsample "casino" "en"
  (position-lat-lon 33.749495 -117.873221)
  (viewport :maxx -117.308 :maxy 36.5515 :minx -118.718 :miny 35.279)
  (list (relevant "Crystal Casino & Hotel" '("building")
                  (position-lat-lon 33.87517 -118.220612))
        (relevant "The Bicycle Casino" '("landuse-commercial" "amenity-casino")
                  (position-lat-lon 33.966085 -118.166707)
                  :house-number "7301")
        (relevant "The Commerce Casino" '("amenity-casino")
                  (position-lat-lon 33.998295 -118.144928)
                  :house-number "6131")
        (relevant "Commerce Casino" '("amenity-casino")
                  (position-lat-lon 34.000141 -118.143703))
        (relevant "Hollywood Park Casino" '("building" "amenity-casino")
                  (position-lat-lon 33.947588 -118.33938))
        (relevant "San Manuel Indian Bingo and Casino" '("tourism-attraction" "amenity-casino")
                  (position-lat-lon 34.150149 -117.227594))))

(scoped-samples ("en"
                 (position-lat-lon 55.688087 37.590087)
                 (viewport :maxx 37.592 :maxy 67.3444 :minx 37.5883 :miny 67.3416))

                (def "bank "
                    (list (relevant "" '("building" "amenity-bank")
                                    (position-lat-lon 55.688664 37.59321)
                                    :house-number "20А")))
                (def "химки "
                    (list (vital "Химки" '("place-city")
                                 (position-lat-lon 55.889289 37.444994))))
                (def "Коломенское "
                    (list (vital "Музей-заповедник \"Коломенское\"" '("leisure-park")
                                 (position-lat-lon 55.660829 37.669019))))
                (def "новаторов 14 "
                    (list (relevant "" '("building")
                                   (position-lat-lon 55.667576 37.523191)
                                   :house-number "14 к1")
                          (relevant "" '("building")
                                    (position-lat-lon 55.667156 37.523081)
                                    :house-number "14 к2")))
                (def "пушкин "
                    (list (vital "Пушкин" '("place-city")
                                 (position-lat-lon 59.722262 30.415717))
                          (relevant "Пушкин" '("historic-memorial")
                                    (position-lat-lon 55.749956 37.587827))
                          (relevant "A. C. Пушкин" '("historic-memorial")
                                    (position-lat-lon 55.755464 37.612809))))

                ; A strange museum in Smolensk (near shop centre
                ; "Пушкинский") is reported here.
                (def "пушкинский музей "
                    (list (irrelevant "Музей-заповедник, отдел истории" '("tourism-museum")
                                      (position-lat-lon 54.782396 32.049999))))
                (def "калуга "
                    (list (vital "Калуга" '("place-city-capital-4")
                                 (position-lat-lon 54.510112 36.259801))))
                (def "ленинский "
                    (list (relevant "Ленинский проспект" '("hwtag-nofoot" "hwtag-oneway" "highway-primary")
                                    (position-lat-lon 55.700622 37.567642))
                          (relevant "Ленинский проспект" '("hwtag-lit" "hwtag-nofoot" "hwtag-oneway" "highway-secondary")
                                    (position-lat-lon 55.697408 37.562625)))))

(scoped-samples ("en" (position-lat-lon 55.643109 37.58908)
                      (viewport :minx 36.782572394712019559 :miny 66.470419751926755225
                                :maxx 38.395587605287985866 :maxy 68.064943854992364436))
                (def "рио "
                    (list (vital "ТЦ РИО" '("building" "shop-mall")
                                 (position-lat-lon 55.689754 37.602154)
                                 :house-number "1")
                          (vital "Рио" '("building" "shop-mall")
                                 (position-lat-lon 55.663783 37.51131)
                                 :house-number "109")
                          (relevant "Рио де Пиво" '("amenity-cafe")
                                    (position-lat-lon 55.6831596 37.6251419)))))

(scoped-samples ("ru" *moscow-position* *moscow-viewport*)
                (def "Россия "
                    (list (vital "Россия" '("place-country")
                                 (position-lat-lon 64.6863141 97.7453086))))
                (def "Lesotho"
                    (list (vital "Lesotho" '("place-country")
                                 (position-lat-lon -29.6039311 28.3350096))))
                (def "San Marino"
                    (list (vital "San Marino" '("place-country")
                                 (position-lat-lon 43.9458555 12.4583045))
                          (vital "Città di San Marino" '("place-town")
                                 (position-lat-lon 43.9363997 12.4467173))))
                (def "Cyprus"
                    (list (vital "Κύπρος" '("place-country")
                                 (position-lat-lon 34.9823169 33.1451336))))
                (def "Korea, North"
                    (list (vital "North Korea" '("place-country")
                                 (position-lat-lon 40.3124091 127.3999867))))
                (def "Винзавод "
                    (list (vital "Винзавод" '("amenity" "landuse-commercial")
                                 (position-lat-lon 55.7559047 37.6656405))))
                (def "Камышин спортивная 6"
                    (list (vital "" '("building")
                                 (position-lat-lon 50.0895369 45.3833644)
                                 :house-number "6")
                          (relevant "МОУ СОШ № 6" '("amenity-school")
                                    (position-lat-lon 50.0884958 45.3850127))))
                (def "Санкт-Петербург"
                    (list (vital "Санкт-Петербург" '("place-city-capital-3")
                                 (position-lat-lon 59.9387345 30.3162396)))))

(dolist (query (list "ресторан пушкинъ " "ресторан пушкин" "кафе пушкинъ"))
  (defsample query "ru"
    *skylight-position*
    *skylight-viewport*
    (list (vital "Пушкинъ" '("building" "amenity-restaurant")
                 (position-lat-lon 55.7637177 37.6050293)
                 :house-number "26А")
          (vital "Пушкинъ" '("amenity-cafe")
                 (position-lat-lon 55.7634114 37.6046713)
                 :house-number "26/5"))))

(defsample "restaurant" "en"
  *moscow-airport-station-position*
  *moscow-airport-station-viewport*
  (list (vital "Кофе Хауз" '("internet_access-wlan" "amenity-cafe")
               (position-lat-lon 55.8004875 37.5333406))
        (vital "IL Патио" '("amenity-restaurant")
               (position-lat-lon 55.7994352 37.5327398))
        (vital "Амиго Мигель" '("amenity-restaurant")
               (position-lat-lon 55.7994925 37.5326057))
        (vital "Марукамэ" '("amenity-restaurant")
               (position-lat-lon 55.799595 37.5323589))
        (vital "Пироговая Штолле" '("internet_access-wlan" "amenity-cafe")
               (position-lat-lon 55.8007996 37.5326942))))

(scoped-samples ("en" *moscow-airport-station-position* *moscow-airport-station-viewport*)
                ; A group of buildings with complex numbers.
                (def "Ореховый бульвар 10к2"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.6080474 37.7078451)
                                 :house-number "10 к2 с2")
                          (vital "" '("building")
                                 (position-lat-lon 55.6075383 37.707082)
                                 :house-number "10 к2")))
                (def "Ореховый бульвар 10к2 с2"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.6080474 37.7078451)
                                 :house-number "10 к2 с2")))
                (def "садовая-кудринская 26/40 с2"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.7633065 37.5886129)
                                 :house-number "26/40 с2")))
                (def "садовая-кудринская 26/40 с3"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.7635306 37.5889817)
                                 :house-number "26/40 с3")))
                (def "волков переулок 7/9 с2"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.7626048 37.5735013)
                                 :house-number "7/9 с2")))
                (def "1-й Новокузнецкий переулок, 26/8 с5"
                    (list (vital "" '("building")
                                 (position-lat-lon 55.7352221 37.6321491)
                                 :house-number "26/8 с5")))

                ; A group of villages in Tula oblast.
                (dolist (region (power-set '("россия" "тульская область")))
                  (def (join-strings (cons "Крапивна" region))
                      (list (vital "Крапивна" '("place-village")
                                   (position-lat-lon 53.940985 37.1548407))))
                  (def (join-strings (cons "Пришня" region))
                      (list (vital "Пришня" '("place-village")
                                   (position-lat-lon 53.9291076 37.3122997))))
                  (def (join-strings (cons "Щёкино" region))
                      (list (vital "Щёкино" '("place-town")
                                   (position-lat-lon 54.0044567 37.5179073))))))

;;; Different Hermitage-related queries.
(scoped-samples ("en" *moscow-position* *moscow-viewport*)
                (def "Эрмитаж"
                    (list (vital "Сад Эрмитаж" '("leisure-park")
                                 (position-lat-lon 55.7707567 37.6091465))
                          (vital "Павильон \"Эрмитаж\"" '("building" "tourism-attraction")
                                 (position-lat-lon 55.7373619 37.8078016))))
                (dolist (query '("Эрмитаж Пете" "Эрмитаж Петербург"))
                  (def query
                      (list (vital "Государственный Эрмитаж (Главный штаб Восточное крыло)"
                                   '("building" "tourism-museum")
                                   (position-lat-lon 59.938567 30.3183096)
                                   :house-number "6-8")
                            (vital "Государственный Эрмитаж" '("tourism-museum")
                                   (position-lat-lon 59.9409881 30.3129948))
                            (relevant "Новый Эрмитаж" '("building")
                                      (position-lat-lon 59.9413851 30.3172474)
                                      :house-number "35")
                            (relevant "Малый Эрмитаж" '("building")
                                      (position-lat-lon 59.9411941 30.3155697 )
                                      :house-number "36")
                            (relevant "Большой Эрмитаж" '("building")
                                      (position-lat-lon 59.9418994 30.315939)
                                      :house-number "34")
                            (relevant "Павильон \"Эрмитаж\"" '("building")
                                      (position-lat-lon 59.7135334 30.4033383))
                            (relevant "Эрмитаж" '("building" "tourism-hotel")
                                      (position-lat-lon 59.9233988 30.343724)
                                      :house-number "10")
                            (relevant "дворец \"Эрмитаж\"" '("building" "tourism-museum")
                                      (position-lat-lon 59.88895 29.9033424))
                            (relevant "Эрмитаж" '("shop-gift")
                                      (position-lat-lon 59.7974888 30.2682368))))))

(defsample "метро рев" "ru"
  *minsk-position*
  *minsk-viewport*
  (list (vital "Площадь Революции" '("railway-subway_entrance-moscow")
               (position-lat-lon 55.7564118 37.6233609))
        (relevant "Площадь Революции; Театральная" '("entrance" "railway-subway_entrance-moscow")
                  (position-lat-lon 55.7567031 37.6195548))))

(defsample "Idaho" "en"
  *minsk-position*
  *minsk-viewport*
  (list (vital "Idaho" '("place-state-USA")
               (position-lat-lon 43.6447598 -114.0154188))))

(defsample "Карелия" "en"
  *minsk-position*
  *minsk-viewport*
  (list (vital "Карелия" '("place-state")
               (position-lat-lon 62.6193993 33.4920184))))

(defsample "igema" "en"
  (position-lat-lon 51.8878412 7.5803997)
  (viewport :maxx 8.3167 :maxy 61.6372 :minx 6.8440 :miny 60.1792)
  (list (vital "Igema" '("building")
               (position-lat-lon 51.8878412 7.5803997)
               :house-number "1")))

(defsample "burg metternich " "en"
  (position-lat-lon 50.1058386 7.2378164)
  (viewport :maxx 7.2447 :maxy 58.0872 :minx 7.22865 :miny 58.0669)
  (list (vital "Burg Metternich" '("historic-castle")
               (position-lat-lon 50.1088593 7.2392299))))

(defsample "мороженое" "ru"
  *zelenograd-position*
  *zelenograd-viewport*
  (list (relevant "Мороженое" '("shop")
                  (position-lat-lon 55.9845636 37.1522738))
        (relevant "Мороженое" '("amenity" "shop-kiosk")
                  (position-lat-lon 55.9736582 37.1624689))))

(defsample "кафе юность" "ru"
  *moscow-position*
  *moscow-viewport*
  (list (vital "Юность" '("amenity-restaurant")
               (position-lat-lon 55.7697202 37.6254771)
               :house-number "2")))

(defsample "кафе " "ru"
  (position-lat-lon 55.6613499 37.6333682)
  (viewport :maxx 37.6361 :maxy 67.2982 :minx 37.6306 :miny 67.2926)
  (list (vital "Усадьба принца" '("amenity-restaurant")
               (position-lat-lon 55.6613499 37.6333682))
        (relevant "Il Патио" '("amenity-restaurant")
                  (position-lat-lon 55.6641957 37.6273976))
        (relevant "Cтарбакс" '("amenity-cafe")
                  (position-lat-lon 55.6645603 37.6281835))))

(defsample "гостиница " "ru"
  (position-lat-lon 55.6613499 37.6333682)
  (viewport :maxx 37.6361 :maxy 67.2982 :minx 37.6306 :miny 67.2926)
  (list (vital "Hotel Duet" '("tourism-hotel")
               (position-lat-lon 55.6616465 37.6469482))))

(defsample "магнит " "ru"
  (position-lat-lon 55.6613499 37.6333682)
  (viewport :maxx 37.6361 :maxy 67.2982 :minx 37.6306 :miny 67.2926)
  (list (vital "Магнит" '("shop-supermarket")
               (position-lat-lon 55.6535784 37.6080964))
        (relevant "Магнит" '("shop-convenience")
                  (position-lat-lon 55.6406377 37.6579989)
                  :house-number "19 к3")
        (relevant "\"Магнит\"" '("building" "shop-convenience")
                  (position-lat-lon 55.633934 37.6043427))))

(defsample "детский мир " "ru"
  (position-lat-lon 55.6613499 37.6333682)
  (viewport :maxx 37.6361 :maxy 67.2982 :minx 37.6306 :miny 67.2926)
  (list (vital "Детский Мир" '("shop-toys")
               (position-lat-lon 55.7054891 37.6376839))
        (vital "Детский мир" '("shop-toys")
               (position-lat-lon 55.6225043 37.6676576))))

(defsample "пятерочка " "ru"
  (position-lat-lon 55.6613499 37.6333682)
  (viewport :maxx 37.6361 :maxy 67.2982 :minx 37.6306 :miny 67.2926)
  (list (vital "Пятёрочка" '("shop-supermarket")
               (position-lat-lon 55.6657373 37.650698))
        (relevant "Пятерочка" '("building" "shop-supermarket")
                  (position-lat-lon 55.656211 37.607834))))

;;; Position near СК Олимпийский
(defsample "гостиница " "ru"
  (position-lat-lon 55.781 37.626)
  (viewport :maxx 37.63 :maxy 67.5107 :minx 37.6229 :miny 67.5053)
  (list (vital "СК \"Олимпийский\"" '("tourism-hotel")
               (position-lat-lon 55.7826394 37.6266707))
        (relevant "Slavyanka" '("tourism-hotel")
                  (position-lat-lon 55.7805805 37.6194985))
        (relevant "AZIMUT Hotel Olympic Moscow" '("sponsored-booking" "tourism-hotel")
                  (position-lat-lon 55.7850737 37.6239671))))

;;; Position near Montreal, Canada.
(scoped-samples ("en"
                 (position-lat-lon 45.4955 -73.5370)
                 (viewport :maxx -73.9 :maxy 51.1 :minx -74.0 :miny 51))

                (dolist (query '("notre-dame-de-l'ile-perrot "
                                 "notre-dame perrot "
                                 "l'Île-Perrot "))
                  (def query
                      (list (vital "Notre-Dame-de-l'Île-Perrot" '("place-suburb")
                                   (position-lat-lon 45.3516639 -73.9029686))))))

;;; There are several Londons on the World map, one of them is located
;;; in Canada, state Ontario. And there is a Stevenson Avenue in the
;;; city.
(defsample "Stevenson Avenue London" "en"
  (position-lat-lon 42.98901 -81.19323)
  (viewport :maxx -81.129 :maxy 47.7621 :minx -81.2715 :miny 47.652)
  (list (vital "Stevenson Avenue" '("highway-residential")
               (position-lat-lon 42.98846 -81.1935105))))

(defsample "Plaßstraße 4 14165" "en"
  (position-lat-lon 52.5170364 13.3888593)
  (viewport :maxx 13.3915 :maxy 61.9339 :minx 13.3863 :miny 61.928)
  (list (vital ""  '("building-address")
               (position-lat-lon 52.4156159 13.2636967)
               :house-number "4")
        (relevant "" '("building-address")
                  (position-lat-lon 52.4157795 13.2636457)
                  :house-number "4A")
        (relevant "" '("building-address")
                  (position-lat-lon 52.4157386 13.2632246)
                  :house-number "4B")))

(defsample "Мазурова 14" "ru"
  *minsk-position*
  *minsk-viewport*
  (list (vital "" '("building")
               (position-lat-lon 53.8973455 27.4250898)
               :house-number "14")
        (irrelevant "" '("building")
                    (position-lat-lon 53.9145531 27.5746485)
                    :house-number "14")))

(dolist (query '("никольская 25" "никольская 25 "))
  (defsample query "ru"
    *moscow-airport-station-position*
    *moscow-airport-station-viewport*
    (list (vital "Nautilus shopping center"
                 '("building" "shop-mall" "sponsored-banner-lamoda_ru")
                 (position-lat-lon 55.7591572 37.6247583)
                 :house-number "25")

          ; A group of relevant results from Moscow satellite cities
          ; (Рыбное, Рыбинск and Железногорск, in order).
          (relevant "" '("building")
                    (position-lat-lon 54.7011511 39.5314428)
                    :house-number "25")
          (relevant "" '("building")
                    (position-lat-lon 58.0546492 38.8921517)
                    :house-number "25")
          (relevant "" '("building")
                    (position-lat-lon 52.3326383 35.3358952)
                    :house-number "25")

          (irrelevant "Hostel on Leningradskoe Shosse 25/1"
                      '("sponsored-booking" "tourism-hostel")
                      (position-lat-lon 55.8269943 37.4888106)
                      :house-number "25/1"))))

(defsample "london" "en"
  *moscow-position*
  *moscow-viewport*
  (list (vital "London" '("place-city-capital-2")
               (position-lat-lon 51.5073179 -0.1276517))))

(defsample "new york" "en"
  *moscow-position*
  *moscow-viewport*
  (list (vital "New York" '("place-city")
               (position-lat-lon 40.7305963 -73.9865987))))

(defsample "горького 1" "ru"
  *hrodna-position*
  *hrodna-viewport*
  (cons (vital "" '("building")
               (position-lat-lon 53.6861244 23.8312382)
               :house-number "1")
        (loop
           for position in (list (position-lat-lon 53.6863976 23.8308586)
                                 (position-lat-lon 53.68557 23.8319221)
                                 (position-lat-lon 53.6858218 23.8315694))
           for index = 1 then (1+ index)
           collecting (relevant "" '("building")
                                position
                                :house-number (format nil "1/~a" index)))))

(defsample "проспект независимости" "ru"
  *minsk-position*
  *minsk-viewport*
  (mapcar (lambda (position)
            (vital "praspiekt Niezaliežnasci"
                   '("psurface-paved_good" "hwtag-nobicycle" "hwtag-nofoot" "hwtag-oneway"
                     "highway-primary")
                   position))
          (list (position-lat-lon 53.9010958 27.5599433)
                (position-lat-lon 53.9267342 27.6230016))))
