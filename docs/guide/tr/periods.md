# Dönem sütunları

Dönemlere göre buluntu grafiği ancak dönemler zaman sırasıyla dizildiğinde okunabilir. Bir tablo programı `Erken Tunç Çağı`, `Geç Tunç Çağı`, `Helenistik`, `Neolitik` değerlerini alfabetik sıralar; bu da Neolitik'i Helenistik'ten sonraya koyar. Chart-er dönem içeren bir sütunu tanır, ona **dönem** türünü verir ve onu kullanan her grafiği eskiden yeniye doğru sıralar.

Bunun için bir şey yapmanız gerekmez. Bu sayfa Chart-er'in ne yaptığını ve bunun nasıl düzeltileceğini anlatır.

## Neler tanınır

- Türkçe, İngilizce ve Almanca **dönem adları**: `Geç Tunç Çağı`, `Late Bronze Age`, `Frühbronzezeit`, `Helenistik`.
- **Kısaltmalar ve evreler**: `EB II`, `LH IIIC`, `GTÇ`, `LN`.
- **Hücreye yazılmış tarihler**: `MÖ 1500`, `1500 BC`, `M.S. 200`, `9000 BP`, `1500-1200 BC`, `MÖ 5. yüzyıl`, `5th century BC`, `MÖ 3. binyıl`.
- **Aralıklar ve seçenekler**: `LN-FN`, `EM I-III`, `LH IIIB-C`, `Late Neolithic or LN`.

Tarihin bilinmediğini söyleyen değerler (`Bilinmiyor`, `Karışık`, `Unknown`, `Mixed`) sona konur.

`-1500` gibi düz yıllardan oluşan bir sütun sayı sütunudur ve zaten doğru sıralanır.

## Tarihler nereden gelir

Dönem adları, yayımlanmış literatürden alınmış dönem tanımlarının açık dizini olan [PeriodO](https://perio.do)'dan tarihlenir. Chart-er bu dizinin kendi kopyasını taşır; dosya yüklediğinizde perio.do'ya bağlanılmaz.

Aynı ad farklı yerlerde farklı yıllar demektir: Anadolu'nun Erken Tunç Çağı, Britanya'nınki değildir. Chart-er bu yüzden sütunu bir bütün olarak okur, değerlerinin çoğu için tanım bulunan bölgeyi belirler ve her değeri o bölgeye göre tarihler.

Veri seti sayfasında bir dönem sütununda **Sıra ve kaynaklar**'a basarak her değer için şunları görürsünüz:

- hangi yılların verildiği,
- nasıl bağlandığı: yazıldığı gibi bulundu, kısaltma açıldı, çevrildi, bir dönemin parçası olarak alındı, etiketteki tarihten okundu, kendi verinizden alındı ya da modelinizden geldi,
- hangi yayımlanmış tanımın kullanıldığı ve bu tanımın PeriodO kaydına bağlantı.

Bir grafiği sunmadan önce bakılacak yer burasıdır. **Yerleştirilemedi, sonda sıralanır** diye işaretlenen bir değer anlaşılamamıştır.

## Düzeltmek

Bunların hepsi veri seti sayfasında, **Sıra ve kaynaklar** altındadır. Her birinden sonra veri seti yeniden okunur ve sonradan yapılan grafikler yeni sırayı kullanır. Var olan bir grafik, siz onu revize edene kadar yapıldığı sırayı korur.

**Bir değerin anlamını yazın.** Değerin yanında, **Anlamı** altına dönemin olağan adını ya da bir tarih yazın: `ECh`, `Early Chalcolithic` demektir; `Evre 7`, `720-650 BC` demektir. **Anlamları kaydet**'e basın. Bunu hiçbir dizinin bilmediği kazı kısaltmaları için kullanın.

**Kendi tablonuzdaki tarihleri kullanın.** Veri setinde her satırın başlangıç ve bitiş yılını tutan sütunlar varsa **Tarihleri sütunlardan al**'a basıp bunları seçin. Her dönem, kendi satırlarındaki en erken başlangıç ve en geç bitişe göre yerleştirilir. Tablonuzda `1500`, MÖ 1500 anlamına geliyorsa *Yıllar MÖ sayılıyor* kutusunu işaretleyin. Kendi tarihleriniz PeriodO'dan önce gelir.

**Bütün sırayı yazın.** Panelin altında, *Ya da bütün sırayı elle yazın*: her satıra bir değer, en eski en üstte. Hiçbir yerde tarihi bulunmayan, tek bir yerleşime ait evreler (`Evre 1`, `Evre 2a`) için doğrudan yol budur.

**Modelinize sorun.** *Yerleştirilemeyen değerleri modele sor*, yalnızca bu sütunun farklı değerlerini Ayarlar'daki modele gönderir ve bunların hangi dönemler olduğunu sorar. Grafik yapmak dışında, Chart-er'de modele bir şey gönderen tek düğme budur ve göndermeden önce sorar. Yanıt, diğer adlar gibi PeriodO'da aranır; yalnızca modelin önerdiği yıllar tahmin olarak işaretlenir.

**Kapatın ya da açın.** *Dönem değil*, sütunu yeniden düz metne çevirir. Chart-er dönem içeren bir sütunu tanımadıysa **Dönem olarak işle** bunu zorlar.

## Bir sütun tanınmadığında

Chart-er temkinlidir: bir kronoloji uydurmaktansa sütunu metin olarak bırakmayı yeğler. Bir sütun ancak değerlerinin çoğu tarihlenebildiğinde ve en az biri kuşkuya yer bırakmayacak biçimde tarihlendiğinde dönem sütunu olur. Bunu söyleyen bir başlık (`Dönem`, `Evre`, `Period`, `Phase`) eşiği düşürür; çünkü gerçek dönem sütunları yerel kısaltmalarla doludur. 200'den fazla farklı değeri olan bir sütun hiçbir zaman dönem sayılmaz.

Yani sütununuz tanınmadıysa: sütunun adını `Dönem` ya da `Period` yapın, ya da **Dönem olarak işle**'ye basıp yerleştirilemeyen değerlerin anlamlarını doldurun.

## Grafikte

Modele yalnızca sütunun bir dönem sütunu olduğu söylenir. Sıra gönderilmez. Chart-er sırayı model yanıt verdikten sonra grafiğe kendisi koyar ve bunu grafiğin düzeltmeleri altında listeler. Ters çevirmek için istekte `en yeni önce` deyin.
