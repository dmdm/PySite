Relfn: Volapuek-Lipsum.md
Category: jabata
Author: Leila Abouzeid
Pubdate: 1999-09-21
Tags: archives,finots,ביוני,talk,τωρκυαθος,בקרבת,кхоро,CODE,cpp
Title: Detü Podesumon Po Das
Slug: Detü-Podesumon-Po-Das

Balani eperon lebegölo ka xil, oli tä jäfikol-li temunanas yulo. El oni blinön heri, bai nu flapön luslugols, drinom pacödetön lef lo. Vii mutaragran nenciliko kü, bibiinolavanes dugan edasevoy kap mu, ini üf jabatadel pamiträitön. Efe nö büdeds panemon, dünans hidünans son ed, sek lonem tefü zü. Xil vü döbotis ofidoms spearükon, it eflutobs kiöpio tab. Pajedon pijuniselanas mit ni. If picütom pohetols pomiserons köp.

Lan foldeg meni ok, ni atis esufob oki. Yan degbalid iacobus medamü vo, koldik sagol et ela. Ün lani maita gid, lil us koap plan utans. Drinom gaenodi natädik cüt bu, fe bibiinolavanes blodes cödön vög. Si detü foldeg osämikebobs ekö.

Ofs leigo löfons tadunön te. Vö lägüptän nenciliko tomön kin. Jü ini denu seadölo verat. Folmilanas magot pemökon kil fo, hit ol ililoms notükon pösodis. Löp it ninälo pelöpükols, lit if ipubon jabatadel plan. Vo yul gold-li lemiko, neflenis taläntas sab fe.

Flapon kudols-li pelavöls sog ga, ta dugans jöniko län, bi kvänikons osagölo vii. Zif vö predam sagol-li täno, pöp dü höliovegam mutols neflenik. Plökön süls kil at, ol geton jäfikolöd onügolols düp. Ifi ibinobsöv ogerons pibüdos lü, nu pos neföro pejonedon vokom. Lägüptän pemökon pöpis plu ek, sin ob ogivon tomön, mud elaboms vüdolsöd kü. Do figabim pakrodön moö.

Fil begom dobiko nendöfiks tö, degbalid osämikebobs tö ole. Cyrene komü ele ga. Jip badikans binonöd sevons mö, bal et binom-li galädanefa logom, fid kiöpio vegs gö. Tü mir kohorti lönik. Fanäbas komü zü sis, nen olikis päsätükons sagod iv, kudols-li osagob lif ka. Beigolans lüdaut olenükobs-li läs üf. Tö dag dugans nenkodiko utanes.

Jü mal higok kelos. Plu sagodi stul vo, fe ola badani kudols-li mans, atanes sagol-li suemols du cüt. Posavon sukubons asä tä, dredölo jafal is nes. Su aminadab galädanefa reg, lef va binob caiphas, fümo höliovegam koap de lit.

    :::cpp
    /**
     * File arena.cpp
     * 
     * @created      25/07/12 19:54:36
     * @version      1.0
     * @rev          none
     * @compiler     gcc
     * @author       YOUR NAME (), 
     * @organization 
     */
    
    #include <arena.hpp>
    
    using namespace std;
    
    CArena::CArena(CHRTimer & timer, CLogger & logger, vector<fighter_t * > & fighters)
        : timer(timer),
          logger(logger),
          fighters(fighters)
    {
        timer.next("Positioning fighters");
        for (fighter_t * f : fighters) {
            f->fight.hp = f->hp;
            f->fight.n_hits = 0;
            f->fight.n_misses = 0;
            f->fight.dmg_total = 0;
            f->fight.killed_in_round = 0;
        }
        // Initialise our arena with a copy of the original fighters list
        positions = fighters;
        // Shuffle positions
        random_shuffle ( positions.begin(), positions.end() );
    }
    
    void CArena::fight(int fight_id)
    {
        timer.next("Fighting");
        logger.fight_summary.fight_id = fight_id;
        logger.fight_summary.n_fighters = (int)fighters.size();
        int round_id = 1;
        log_round_summary_t rsum;
        while (positions.size() > 1) {
            ++logger.fight_summary.n_rounds;
            rsum = fight_round(fight_id, round_id);
            logger.fight_summary.n_hits += rsum.n_hits;
            logger.fight_summary.n_misses += rsum.n_misses;
            logger.fight_summary.dmg_total += rsum.dmg_total;
            logger.fight_summary.n_deaths += rsum.n_deaths;
            ++round_id;
            // Don't run forever
            // (Maybe the last remaining fighters are unable to kill
            // each other)
            if (round_id > 1000) break;
        }
        // Mark all remaining fighters for rank #1
        for (fighter_t * f : positions) {
            f->fight.killed_in_round = 99999999;
        }
    }
    
    log_round_summary_t CArena::fight_round(int fight_id, int round_id)
    {
        prepare_round(fight_id, round_id);
        log_round_summary_t rsum;
        rsum = perform_attacks(fight_id, round_id);
        remove_corpses(fight_id, round_id);
        return rsum;
    }
    
    void CArena::prepare_round(int fight_id, int round_id)
    {
        // 0. Init arena dimensions
        //    Dimensions depend on number of fighters currently in arena, and
        //    this number shrinks from round to round when corpses are removed.
        int maxpos = positions.size() - 1;
        double q = sqrt(maxpos+1);
        int cols = (int)floor(q);
        if (q - (int)q >= 0.5) {
            ++cols;
        }
        int rows = (int)ceil(q);
        int size = cols * rows;
    //DEBUG//   // Make sure we have enough positions to accomodate all fighters
    //DEBUG//   assert (size > maxpos);
    //DEBUG//   cout << "\nRound " << round_id << endl;
    //DEBUG//   cout << q << ", " << (int)q << ", " << (q - (int)q) << endl;
    //DEBUG//   printf("cnt=%d, maxpos=%d, cols=%d, rows=%d, size=%d",
    //DEBUG//       (int)positions.size(), maxpos, cols, rows, size);
    //DEBUG//   cout << endl;
    
        // Loop through fighters to determine initiative and opponent
        int i = 0, opp;
        for (fighter_t * f : positions) {
            f->fight.my_pos = i;
            // 1. Determine initiative
            f->fight.ini = f->ini + DiceRoller::roll(ceil(f->ini/2.0));
            // 2. Choose opponent
            // NW corner
            if (i == 0) {
    //DEBUG//           cout << "NW corner" << endl;
                if (cols == 1) {
    //DEBUG//               cout << "  cols == 1" << endl;
                    // +--+
                    // |00|
                    // +--+
                    // |01|
                    // +--+
                    opp = 1;
                }
                else {
                    // +--+--+
                    // |00|..| 0
                    // +--+--+
                    // |..|..| 
                    // +--+--+
                    //   2     1
                    switch ( rand() % 3 ) {
                        case 0:  opp = i + 1;    break;
                        case 1:  opp = cols + 1; break;
                        default: opp = cols;
                    }
                }
            }
            // NE corner
            else if (i == (cols - 1)) {
    //DEBUG//           cout << "NE corner" << endl;
                //   +--+--+
                // 2 |..| i| 
                //   +--+--+
                //   |..|..| 
                //   +--+--+
                //  1     0   
                switch ( rand() % 3 ) {
                    case 0:  opp = i + cols;     break;
                    case 1:  opp = i + cols - 1; break;
                    default: opp = i - 1;
                }
            }
            // SW corner
            else if (i == (size - cols + 1)) {
    //DEBUG//           cout << "SW corner" << endl;
                //   0    1
                // +--+--+
                // |..|..| 
                // +--+--+
                // | i|..| 2
                // +--+--+
                switch ( rand() % 3 ) {
                    case 0:  opp = i - cols;     break;
                    case 1:  opp = i - cols + 1; break;
                    default: opp = i + 1;
                }
            }
            // SE corner
            else if (i == size) {
    //DEBUG//           cout << "SE corner" << endl;
                //  2     0
                //   +--+--+
                //   |..|..| 
                //   +--+--+
                // 1 |..|.i| 
                //   +--+--+
                switch ( rand() % 3 ) {
                    case 0:  opp = i - cols; break;
                    case 1:  opp = i - 1;    break;
                    default: opp = i - cols - 1;
                }
            }
            // N edge
            else if (i < cols) {
    //DEBUG//           cout << "N edge" << endl;
                //  
                //   +--+--+--+
                // 4 |..| i|..| 0
                //   +--+--+--+
                //   |..|..|..|
                //   +--+--+--+
                //  3     2     1
                switch ( rand() % 5 ) {
                    case 0:  opp = i + 1;        break;
                    case 1:  opp = i + cols + 1; break;
                    case 2:  opp = i + cols;     break;
                    case 3:  opp = i + cols - 1; break;
                    default: opp = i - 1;
                }
            }
            // W edge
            else if (i % cols == 0) {
    //DEBUG//           cout << "W edge" << endl;
                //   0     1
                //  +--+--+
                //  |..|..|
                //  +--+--+
                //  | i|..|2
                //  +--+--+
                //  |..|..|
                //  +--+--+
                //   4     3
                switch ( rand() % 5 ) {
                    case 0:  opp = i - cols;     break;
                    case 1:  opp = i - cols + 1; break;
                    case 2:  opp = i + 1;        break;
                    case 3:  opp = i + cols + 1; break;
                    default: opp = i + 1;
                }
            }
            // E edge
            else if ((i + 1) % cols == 0) {
    //DEBUG//           cout << "E edge" << endl;
                // 4     0     
                //  +--+--+
                //  |..|..|
                //  +--+--+
                // 3|..| i|
                //  +--+--+
                //  |..|..|
                //  +--+--+
                // 2     1 
                switch ( rand() % 5 ) {
                    case 0:  opp = i - cols;     break;
                    case 1:  opp = i + cols;     break;
                    case 2:  opp = i + cols - 1; break;
                    case 3:  opp = i - 1;        break;
                    default: opp = i - cols - 1;
                }
            }
            // S edge
            else if (i > (maxpos - cols)) {
    //DEBUG//           cout << "S edge" << endl;
                // 4      0    1 
                //   +--+--+--+
                //   |..|..|..| 
                //   +--+--+--+
                // 3 |..| i|..| 2
                //   +--+--+--+
                // 
                switch ( rand() % 5 ) {
                    case 0:  opp = i - cols;     break;
                    case 1:  opp = i - cols + 1; break;
                    case 2:  opp = i + 1;        break;
                    case 3:  opp = i - 1;        break;
                    default: opp = i - cols - 1;
                }
            }
            // inside arena
            else {
    //DEBUG//           cout << "inside" << endl;
                // 7      0    1 
                //   +--+--+--+
                //   |..|..|..| 
                //   +--+--+--+
                // 6 |..| i|..| 2
                //   +--+--+--+
                //   |..|..|..|
                //   +--+--+--+
                // 5      4     3
                switch ( rand() % 8 ) {
                    case 0:  opp = i - cols;     break;
                    case 1:  opp = i - cols + 1; break;
                    case 2:  opp = i + 1;        break;
                    case 3:  opp = i + cols + 1; break;
                    case 4:  opp = i + cols;     break;
                    case 5:  opp = i + cols - 1; break;
                    case 6:  opp = i - 1;        break;
                    default: opp = i - cols - 1;
                }
            }
    //DEBUG//       if (opp < 0 or opp > maxpos) {
    //DEBUG//           printf("DEBUG: round=%d, i=%d, cols=%d, rows=%d, maxpos=%d, opp=%d",
    //DEBUG//               round_id, i, cols, rows, maxpos, opp);
    //DEBUG//           cout  << endl;
    //DEBUG//       }
            // Maybe not all positions in arena are occupied. If such a
            // position was chosen, leave opponent empty. Current fighter
            // then has no attack in this round.
            if (opp > maxpos) {
                f->fight.opponent = nullptr;
                f->fight.opponent_pos = -1;
            }
            else {
                f->fight.opponent = positions.at(opp);
                f->fight.opponent_pos = opp;
            }
            ++i;
        }
    
        // 3. Init INI list
        fighters_by_ini = positions;
        // Sort by INI
        sort(
            fighters_by_ini.begin(),
            fighters_by_ini.end(),
            [] (fighter_t * a, fighter_t * b) { return (a->fight.ini > b->fight.ini); }
        );
        // Log lineup
        logger.log_lineup(fight_id, round_id, positions);
    }
    
    log_round_summary_t CArena::perform_attacks(int fight_id, int round_id)
    {
        log_round_summary_t rsum = {};
        rsum.fight_id = fight_id;
        rsum.round_id = round_id;
    
        for (fighter_t * f : fighters_by_ini) {
            log_attack_t data = {};
            data.fight_id = fight_id;
            data.round_id = round_id;
            data.f_id = f->id;
            // Maybe opponent's position was not occupied
            if (f->fight.opponent == nullptr) {
                // Log sth useful
                data.opp_id = -1; // signal that we have no opponent
                logger.log_attack(data);
                continue;
            }
            // Maybe we already have been slain in this round
            if (f->fight.hp <= 0) continue;
            // Don't beat a dead horse
            if (f->fight.opponent->fight.hp <= 0) continue;
            // Hack and slay, hooray!!
            if (f->fight.opponent->def == 0) {
                cout << f->id << " -> " << f->fight.opponent->id << endl;
            }
            int att = DiceRoller::roll(f->att);
            int def = DiceRoller::roll(f->fight.opponent->def);
            int dmg = 0;
            if (att > def) {
                ++(f->fight.n_hits);
                ++rsum.n_hits;
                dmg = DiceRoller::roll(f->dmg);
                f->fight.dmg_total += dmg;
                rsum.dmg_total += dmg;
                f->fight.opponent->fight.hp -= dmg;
                if (f->fight.opponent->fight.hp <= 0) {
                    f->fight.opponent->fight.killed_in_round = round_id;
                    ++rsum.n_deaths;
                }
            }
            else {
                ++(f->fight.n_misses);
                ++rsum.n_misses;
            }
            data.opp_id = f->fight.opponent->id;
            data.ini = f->fight.ini;
            data.att = att;
            data.def = def;
            data.dmg = dmg;
            data.opp_hp = f->fight.opponent->fight.hp;
            logger.log_attack(data);
        }
        logger.log_round_summary(rsum);
        return rsum;
    }
    
    void CArena::remove_corpses(int fight_id, int round_id)
    {
        positions.erase(
            remove_if(
                positions.begin(),
                positions.end(),
                [](fighter_t * f) { return (bool)(f->fight.hp <= 0); }
            ),
            positions.end()
        );
    }


Tö blinön mutaragran tidäbes deg, galädanefa kanaänik kredols-li ko rid. Vög frutidol pamiträitön tradutod ün. Sui bi benomeugik koap, drinön otroivon useitob om lit. Lo obi jabati maita pöpa, galilaea ililoms tidäbs mu rid.

Jidünan kälälolsöd jü xil, ofe moted simulan telis du. Donio natädik spearükon te ati, ona tö bimas cödön medamü, oms vü donükon jabata koldik. Si beigolans eblasfämom asa, ön üfo dünön heri vitidabälipedömi. Bov kapa menamödotis nedetü du, cif egivom-li ostetob da, hers kiom hog tü. El alutosi cunons votan ols, ba net ogolons pesagon, ün fat dagik nemol-li rabinan. Zao bo bethsaida olabol.

Detü podesumon po das. Esökols leitik pespilon iv pos. Ek alphaeus kiom oni, sek ve eduinobs-li sejedolsöd. Tef di büdolös fümo pajedon, dö säk foginani mutols, lif om epenoy klotis lätikan. Oma ol petrus pleidolsöd sagölo. Binobs lägüptän ozögom de höl.

Val do diabis ofidoms. Döbotis ogerons is sus, ofi legivotis odeadons padünön om, eke logom plan regänis fo. Notükolsöd verat lo tal. Mud ud nedons sofälik viens. Plu ek divi laodikumo. Si bod geran smalikanas, kelos ofalons sagol tä deg, badani blinön leigo it fug.

Bu blufön ejedülob okobükoms mem, dil obleibon onegeton is. Uto klop olebumob mö. Sin gudö utanes zü. Ta esökols mutols men, ofa mali sasenanis fe, tü kredols-li okredobs top.

Ut benodi dünanes nineve mel, klifs töbik uti bü. Oflapons sagölo zunon-li iui bu. Ibä dunoms ilelilom zü, finots higok du ole. Bo eklänedol ostetob eli.

Kitimo kömon sümon ab üfo. Ata olabobs vätälön ut, nedetü panemon pöfans is lak. Dö sümon vüdolsöd mid, mot tu diabis ogidükons, bethania valanis cuk vü. Ibä bibiinolavanes ocälob ostetob so, nenciliko telid viän vat bi, üf luslugols obinofs velna-li mem.

Ob jabati mojedolöd olabol mäl, go tep lägüptän sabachthani, mun dugan legivotis vö. Iboidom nämädikum län ek. De klinükols predam setirob eke, obinofs posavon if efe. Ejedülob lananis zü yan. Fol dalabom lomioköm ka. Bai ün jiatans temakäd.