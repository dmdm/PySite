Relfn: Letzebuergesch-Lipsum.md
Category: slave
Author: Евге́ния Соломо́новна Ги́нзбург
Pubdate: 1972-10-27
Tags: bottom,مناوشات,culpa,jabata,instruction,IMAGE,CODE,common-lisp
Title: Gart Schéi D'Stroos Nei Da, Et D
Slug: Gart-Schéi-D-Stroos-Nei-Da--Et-D

As hirem Schiet net. Wielen geplot bessert am ech, Bass rëschten net op, ze Mamm Wisen wéi. Nët wa Faarwen schéinen Plett'len, et rëm geet Dall frou. Un keen fergiess wat, huet d'Musek si méi. Sin Kaffi Léift grouss dé. Dir ke Ierd goung, déi op Hunn drun Riesen, hun Bass gewëss um.

Engem Hémecht wat am, Fréijor d'Blumme dee da. Am kille Blummen der, mat de grousse prächteg. Un sech erem dee, mä hun d'Sonn Himmel Kolrettchen, och mä Welt blénken d'Kàchen. Vun jo rout gréng. Fréijor däischter verstoppen ké dir, si Mamm Riesen Blénkeg dén.

Vill Engel Kirmesdag ech no. Alles ménger derfir mir ze, Stieren blénken der vu. An welle hannendrun mat, si Stad Bass Fielse wéi. Et ech Hären Himmel Fréijor, stolz Schuebersonndeg rëm ke. Koum Schuebersonndeg de rei, oft riede räich Dohannen hu, onser laacht ke dan. No vun aremt wielen, Gart Riesen get et.

![img_0083_800x533.jpg]({{asset_url\('img/blog/img_0083_800x533.jpg'\)}} "Image tag by Markdown: img_0083_800x533.jpg")

Fir as laanscht Margréitchen. Dan op zënter heescht heemlech, rëscht Kléder blénken an hie. Hie as keen gemaacht, wa zum aremt Gaart Feierwon. Mir do Feld Mecht.

Ech brét Grénge muerges hu. Ass Stréi Kléder d'Meereische ze, dat huet fond vu. Och op d'Welt Poufank schnéiwäiss, rifft beschéngt däischter mä blo. Iwerall d'Kirmes hun dé. Mä Ronn erem frou dat. Rem vu iwerall löschteg, d'Beem zwëschen et dan.

Méi deser wielen vu. Um rëm keng Hierz, méi Dach zielen ké, denkt Léift schéinen am wou. Rem d'Land schléit Poufank an, och fu Stad bereet, hire bléit jo nun. Gart schéi d'Stroos nei da, et d'Musek Plett'len net. Dén haut soubal heemlech ze, nun wa Welt Dach d'Margréitchen. Keen Fläiß Kléder oft an.

En Hemecht Blummen get, eng keen d'Pied geplot jo. Ke vun d'Vioule Kirmesdag, Hämmel Faarwen si hin. En séngt Schiet klinzecht gei. Gei mä fort d'Margréitchen, en dan gudden duerch, gét mä Well hinnen Kolrettchen. Ké Kléder Klarinett hie. Dé dén hirem laacht, un blo Wisen Friemd. As lait gudden Hemecht aus, fond drun ménger si den.

De Feld päift dat. Et schlon frësch vun, wa haut d'Sonn ass, Land d'Liewen d'Margréitchen si blo. Sou fu d'Wise uechter, un Dach d'Wéën Minutt fir. Ké brét meescht beschéngt déi, spilt d'Pan och vu.

Drem gemaacht jo ech. Si gréng néierens den. Sin aremt Schied löschteg am. Net sinn sëtzen hu, do hir Hunn Margréitchen. Mä blo d'Wise Plett'len, méngem Minutt as méi.

    :::common-lisp
    (load "graph-util")
    
    (defparameter *congestion-city-nodes* nil)
    (defparameter *congestion-city-edges* nil)
    (defparameter *visited-nodes* nil)
    (defparameter *node-num* 30)
    (defparameter *edge-num* 45)
    (defparameter *worm-num* 3)
    (defparameter *cop-odds* 15)
    
    (defun random-node ()
      (1+ (random *node-num*)))
    
    (defun edge-pair (a b)
      (unless (eql a b)
        (list (cons a b) (cons b a))))
    
    (defun make-edge-list ()
      (apply #'append (loop repeat *edge-num*
                            collect (edge-pair (random-node) (random-node)))))
    
    (defun direct-edges (node edge-list)
      (remove-if-not (lambda (x)
                       (eql (car x) node))
                     edge-list))
    
    (defun get-connected (node edge-list)
      (let ((visited nil))
        (labels ((traverse (node)
                   (unless (member node visited)
                     (push node visited)
                     (mapc (lambda (edge)
                             (traverse (cdr edge)))
                           (direct-edges node edge-list)))))
          (traverse node))
        visited))
    
    (defun connect-with-bridges (islands)
      (print islands)
      (when (cdr islands)
        (append (edge-pair (caar islands) (caadr islands))
                (connect-with-bridges (cdr islands)))))
    
    (defun find-islands (nodes edge-list)
      (let ((islands nil))
        (labels ((find-island (nodes)
                   (let* ((connected (get-connected (car nodes) edge-list))
                          (unconnected (set-difference nodes connected)))
                     (push connected islands)
                     (when unconnected
                       (find-island unconnected)))))
          (find-island nodes))
        islands))
    
    (defun connect-all-islands (nodes edge-list)
      (append (connect-with-bridges (find-islands nodes edge-list)) edge-list))
    
    (defun edges-to-alist (edge-list)
      (mapcar (lambda (node1)
                (cons node1
                      (mapcar (lambda (edge)
                                (list (cdr edge)))
                              (remove-duplicates (direct-edges node1 edge-list)
                                                 :test #'equal))))
              (remove-duplicates (mapcar #'car edge-list))))
    
    (defun add-cops (edge-alist edges-with-cops)
      (mapcar (lambda (x)
                (let ((node1 (car x))
                      (node1-edges (cdr x)))
                  (cons node1
                        (mapcar (lambda (edge)
                                  (let ((node2 (car edge)))
                                    (if (intersection (edge-pair node1 node2)
                                                      edges-with-cops
                                                      :test #'equal)
                                        (list node2 'cops)
                                      edge)))
                                node1-edges))))
              edge-alist))
    
    (defun make-city-edges ()
      (let* ((nodes (loop for i from 1 to *node-num*
                          collect i))
             (edge-list (connect-all-islands nodes (make-edge-list)))
             (cops (remove-if-not (lambda (x)
                                    (zerop (random *cop-odds*)))
                                  edge-list)))
        (add-cops (edges-to-alist edge-list) cops)))
    
    (defun neighbors (node edge-alist)
      (mapcar #'car (cdr (assoc node edge-alist))))
    
    (defun within-one (a b edge-alist)
      (member b (neighbors a edge-alist)))
    
    (defun within-two (a b edge-alist)
      (or (within-one a b edge-alist)
          (some (lambda (x)
                  (within-one x b edge-alist))
                (neighbors a edge-alist))))
    
    (defun make-city-nodes (edge-alist)
      (let ((wumpus (random-node))
            (glow-worms (loop for i below *worm-num*
                              collect (random-node))))
        (loop for n from 1 to *node-num*
              collect (append (list n)
                              (cond ((eql n wumpus) '(wumpus))
                                    ((within-two n wumpus edge-alist) '(blood!)))
                              (cond ((member n glow-worms)
                                     '(glow-worm))
                                    ((some (lambda (worm)
                                             (within-one n worm edge-alist))
                                           glow-worms)
                                     '(lights!)))
                              (when (some #'cdr (cdr (assoc n edge-alist)))
                                '(sirens!))))))
    
    (defun new-game ()
      (setf *congestion-city-edges* (make-city-edges))
      (setf *congestion-city-nodes* (make-city-nodes *congestion-city-edges*))
      (setf *player-pos* (find-empty-node))
      (setf *visited-nodes* (list *player-pos*))
      (draw-city))
    
    (defun find-empty-node ()
      (let ((x (random-node)))
        (if (cdr (assoc x *congestion-city-nodes*))
            (find-empty-node)
            x)))
    
    (defun draw-city ()
      (ugraph->png "city" *congestion-city-nodes* *congestion-city-edges*))
    
    (defun known-city-nodes ()
      (mapcar (lambda (node)
                (if (member node *visited-nodes*)
                    (let ((n (assoc node *congestion-city-nodes*)))
                      (if (eql node *player-pos*)
                          (append n '(*))
                          n))
                    (list node '?)))
              (remove-duplicates 
                  (append *visited-nodes*
                          (mapcan (lambda (node)
                                    (neighbors node *congestion-city-edges*))
                                  *visited-nodes*)))))
    
    (defun known-city-edges ()
      (mapcar (lambda (node)
                (cons node (mapcar (lambda (x)
                                     (if (member (car x) *visited-nodes*)
                                         x
                                       (list (car x))))
                                       (cdr (assoc node *congestion-city-edges*)))))
              *visited-nodes*))
    
    (defun draw-known-city ()
      (ugraph->png "known-city" (known-city-nodes) (known-city-edges)))
    
    (defun new-game ()
      (setf *congestion-city-edges* (make-city-edges))
      (setf *congestion-city-nodes* (make-city-nodes *congestion-city-edges*))
      (setf *player-pos* (find-empty-node))
      (setf *visited-nodes* (list *player-pos*))
      (draw-city)
      (draw-known-city))
    
    (defun walk (pos)
      (handle-direction pos nil))
    
    (defun charge (pos)
      (handle-direction pos t))
    
    (defun handle-direction (pos charging)
      (let ((edge (assoc pos 
                         (cdr (assoc *player-pos* *congestion-city-edges*)))))
        (if edge
            (handle-new-place edge pos charging)
          (princ "That location does not exist!"))))
    
    (defun handle-new-place (edge pos charging)
      (let* ((node (assoc pos *congestion-city-nodes*))
             (has-worm (and (member 'glow-worm node)
                            (not (member pos *visited-nodes*)))))
        (pushnew pos *visited-nodes*)
        (setf *player-pos* pos)
        (draw-known-city)
        (cond ((member 'cops edge) (princ "You ran into the cops. Game Over."))
              ((member 'wumpus node) (if charging
                                         (princ "You found the Wumpus!")
                                         (princ "You ran into the Wumpus")))
              (charging (princ "You wasted your last bullet. Game Over."))
              (has-worm (let ((new-pos (random-node)))
                          (princ "You ran into a Glow Worm Gang! You're now at ")
                          (princ new-pos)
                          (handle-new-place nil new-pos nil))))))
    
    


Dem un ston d'Musek. Frou gehéiert da wéi. Rei an huet dämpen, hu Mamm Milliounen fir, sech d'Sonn Klarinett ke get. Hu wuel d'Leit sou, d'Sonn d'Leit et ons, en schlon d'Vioule net.

De rei Halm d'Blumme. Dé räich Scholl dir. Gin do Gart derfir, rëm fu eise Mecht Blummen, hu esou Poufank méi. Keng däischter op ass, un riede welle Faarwen wat. Am jeitzt gehéiert löschteg rei. En gutt räich bei, zënter gemaacht dat do, welle d'Kanner rëschten wär an.

![images.jpg]({{asset_url\('img/blog/images.jpg'\)}} "Image tag by Markdown: images.jpg")

Well Keppchen néierens wat um. Wou et drun weisen klinzecht, si gét Haus blénken. Nun uechter Plett'len d'Kamäiner ze, nun Dach verstoppen en, dé wéi d'Wéën Hämmel. Onser d'Welt méngem en dem. Do sinn muerges rem, eise zënne dan wa. Da déi lait derfir blénken.

Eng ké sinn Schiet Schuebersonndeg, Biereg soubal Hämmel mä zum. Botze soubal gebotzt am aus. Dén fu Haus Stad laacht, Stad Stieren op sin. Wa ruffen d'Meereische rëm, eng huet ugedon Klarinett en, hire rëscht Hämmel och no. Keen genuch rëschten ons no, Kaffi d'Stroos Kolrettchen et dir.

Op Benn stolz zum, fort duurch hir ké. Wou duerch Fielse Blieder am, Ierd blénken heemlech jo dan. Dee op eise fergiess beschéngt, eraus bereet un dee, get en hale Heck. Am rei Hémecht Feierwon. As haut fest Riesen méi. Mat vu zielen meescht, gutt Blieder Kolrettchen do nei.