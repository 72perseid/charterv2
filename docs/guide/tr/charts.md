# Grafikler

Bir grafik; tek bir veri setinden, üç sütun seçiminden, isteğe bağlı iki ayardan ve bir cümleden yapılır. Model bunları bir grafik tanımına çevirir; Chart-er tanımı denetler ve çizer.

## Form

Bir veri setini açın ve **Yeni grafik** bölümüne gidin.

| Alan | Ne yapar |
|---|---|
| **Başlık** | İsteğe bağlı. Grafik listenizdeki ad. |
| **X ekseni** | Alt kenar boyunca dizilen sütun: çoğunlukla gruplar (dönem, açma, tür) ya da bir tarih. |
| **Y ekseni** | Ölçülen ya da sayılan sütun: bir sayı. |
| **Renk** | İsteğe bağlı. Her grubu ikinci bir sütuna göre böler; örneğin dönem içinde malzeme. |
| **Ne gösterilsin** | Bir grubun Y değerlerinin tek bir işarete nasıl dönüşeceği. Aşağıya bakın. |
| **Yalnızca şu satırlar … eşittir …** | İsteğe bağlı. Grafiği, bir sütunda tek bir değeri taşıyan satırlarla sınırlar. |
| **Grafiği tarif edin** | İsteğiniz, en çok 1 000 karakter. |

İstek kutusunun altındaki satır, modelin bu veri setinden ne göreceğini söyler ([Veri setleri](datasets.md#modelin-gördüğü)).

## Ne gösterilsin

Modele bırakıldığında en sık yanlış giden seçim budur; bu yüzden kendiniz yapabilirsiniz.

| Seçim | Grafik neyi gösterir | Ne için |
|---|---|---|
| **Model karar versin** | modelin cümlenizden ne anladıysa onu | emin değilseniz ya da cümle bunu açıkça söylüyorsa |
| **Toplam** | her grubun Y değerlerinin toplamı | toplanabilen miktarlar: sayımlar, ağırlıklar, alanlar |
| **Ortalama** | her grubun ortalaması | grup başına tipik bir değer |
| **Satır sayısı** | her grupta kaç satır olduğu | her satır bir buluntuysa "dönem başına kaç buluntu" |
| **Dağılım (kutu grafiği)** | her grubun ortancası, çeyrekleri ve aralığı | ölçümler: uzunluklar, genişlikler, indeksler |
| **Her satır bir nokta** | satır başına bir nokta | küçük veri setleri ya da ham değerleri görmek için |

**Ölçümleri toplamayın.** Kırk kemik uzunluğunun toplamı hiçbir şey ifade etmeyen bir sayıdır; yalnızca hangi dönemde daha çok kemik olduğunu gösterir. Bir ölçüm için *Dağılım* ya da *Ortalama* seçin.

Burada ne seçerseniz, model yanıt verdikten sonra grafiğe Chart-er'in kendisi uygular. Model başka bir şey yazdıysa sizin seçiminiz geçerli olur ve fark grafiğin altında listelenir.

## Yalnızca şu satırlar

Bir sütun seçin ve bir değer yazın ya da listeden alın: `Bölge` eşittir `Teselya`. Grafik o zaman yalnızca bu satırları kullanır. Bir dönem sütununda bütün dönemler, bir metin sütununda en sık değerler önerilir; ama sütunda geçen her değer yazılabilir. Hiçbir satırda bulunmayan bir değer hemen reddedilir; böylece bir yazım hatası boş bir grafik üretmez.

Bu, tek bir sütun üzerinde tek bir koşuldur. Daha fazlası için (iki bölge, bir yıl aralığı) bunu istekte söyleyin; model böyle süzgeçler yazabilir, ama yazıp yazmayacağı modele bağlıdır.

## İsteği yazmak

Ne görmek istediğinizi bir meslektaşınıza söyler gibi yazın. Türkçe de İngilizce kadar iyi çalışır.

- `Dönemlere göre toplam buluntu, çubuk grafik`
- `Açmalara göre seramik ağırlığı, mal grubuna göre renkli`
- `Dönemlere göre astragalus uzunluğu dağılımı`
- `Zaman içinde buluntular, çizgi grafik, her malzeme için bir çizgi`
- `Yatay çubuklar, en büyük en üstte`

İşe yarayanlar:

- Sizin için önemliyse **grafik türünü adlandırın**: çubuk, çizgi, nokta, kutu grafiği.
- **Sütun adlarını** veri setinde göründükleri gibi **kullanın**.
- **Her istekte tek grafik.** Chart-er tekil grafikler yapar; yan yana paneller ve üst üste katmanlar desteklenmez.
- **Formun zaten söylediğini yazmayın.** *Dağılım*'ı ve bir süzgeci seçtiyseniz cümlenin bunları yinelemesi gerekmez.

## Grafik sayfası

**Grafik oluştur**'dan sonra sayfa bekler (*Model bekleniyor*, sonra *Model tanımı yazıyor*) ve ardından dört sekme gösterir.

- **Grafik**: çizim.
- **Veri**: arkasındaki satırlar.
- **Tanım**: Vega-Lite JSON'u, grafiğin eksiksiz tarifi.
- **İstek ve yanıt**: modele tam olarak ne gönderildiği ve modelin tam olarak ne yanıt verdiği; model, geçen süre, kullanılan jetonlar ve tahmini maliyetle birlikte.

### Düzeltmeler

Grafiğin altında **Modelin yanıtına uygulanan düzeltmeler**'i görebilirsiniz. Chart-er modelin yanıtını denetlemeden geçirmez. Yaptığı her değişikliği listeler; örneğin:

- bir dönem sütunu kronolojik sıraya kondu,
- modelin yanlış yazdığı bir sütun adı sizin seçtiğinizle değiştirildi,
- toplama biçimi ya da işaret **Ne gösterilsin** seçimine uyduruldu,
- satır süzgeciniz eklendi ya da hiçbir şeyi karşılaştırmayan bir süzgeç kaldırıldı.

Bir grafik sizi şaşırttığında bu listeyi okuyun. Şaşırtıcı olanın modelden mi, bir düzeltmeden mi geldiğini söyler.

Veri setinizle hiç ilgisi olmayan bir yanıt (iki eksen de var olmayan sütunları kullanıyor) onarılmaz, reddedilir. Revizyon o zaman nedeniyle birlikte *Başarısız* görünür.

## Revizyonlar

Bir grafik bir dizi revizyondur. **Revize et** altında sütunları, seçimleri ya da cümleyi değiştirip **Revizyon oluştur**'a basın. Model önceki tanımı da alır; bu yüzden `çubukları yatay yap` ya da `logaritmik ölçek kullan` yalnızca onu değiştirir.

- Yandaki liste her revizyonu isteği ve durumuyla gösterir. Bakmak için birine tıklayın.
- **Bunu geçerli revizyon yap**, grafiğin varsayılan olarak hangisini göstereceğini belirler.
- Yeni revizyon, o an baktığınız revizyondan başlar; yani 2. revizyona dönüp oradan dallanabilirsiniz.
- Hiçbir şeyin üzerine yazılmaz. Başarısız bir revizyon nedeniyle birlikte listede kalır.

Saatte 60 revizyon yapabilirsiniz.

## Dışa aktarma

- Sunumlar ve belgeler için **PNG**, baskı ve bir çizim programında düzenleme için **SVG**.
- **Tanım JSON**: Vega-Lite tanımı; [Vega düzenleyicisinde](https://vega.github.io/editor/) açmak ya da kendi sayfanızda kullanmak için. Veri içermez; satırları `main` adı altında verin.
- **Yeniden üretilebilirlik paketi**: grafiğin tam kaydı. Bkz. [Yeniden üretilebilirlik](reproducibility.md).

## Chart-er'in yapmadıkları

- Tek grafikte birden çok grafik (paneller, katmanlar, çubukların üzerinde çizgi).
- Toplam, ortalama, ortanca ve sayım dışındaki istatistikler: test yok, regresyon çizgisi yok.
- Verinizi değiştirmek. Kategorileri yeniden kodlamak ya da birleştirmek için dosyayı düzenleyip yeniden yükleyin.
