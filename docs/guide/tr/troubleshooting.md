# Sorun giderme

Chart-er bir şeyin neden başarısız olduğunu söyler. İletiyi burada bulun; ekrandaki ifade ayrıntılarla devam edebilir. Hata iletileri İngilizcedir; aşağıda ekranda göründükleri gibi yazılmıştır.

## Yükleme

| İleti | Ne yapmalı |
|---|---|
| *Old Excel (.xls) files are not supported.* | Dosyayı açıp `.xlsx` olarak kaydedin. |
| *Unsupported file type.* | Tabloyu `.csv` ya da `.xlsx` olarak dışa aktarın. |
| *The file has … rows; the limit is 100,000.* / *… columns; the limit is 200.* | Tabloyu grafiğin gerektirdiği kadarına indirin. |
| *The file is empty.* / *The file has a header but no data rows.* | Sayfada ya da dosyada tablo yok. Excel'de doğru sayfanın okunduğunu kontrol edin. |
| *Every sheet in the workbook is empty.* | Aynısı; çalışma kitabı yalnızca grafik ya da özet tablo içeriyor olabilir. |
| *Header row … is past the end of the sheet.* | Başlık satırı 0'dan sayılır. Daha küçük bir sayı girin. |

**Tablo yüklemeden sonra yanlış görünüyor**

- *Her şey tek sütunda.* Ayırıcı bulunamadı. Dosyayı `.xlsx` olarak ya da virgüllü ya da noktalı virgüllü CSV olarak kaydedin.
- *Türkçe harfler bozuk.* Dosyayı UTF-8 olarak kaydedip yeniden yükleyin.
- *Bir sayı sütunu "metin".* Bazı hücreler sayı değil (`?`, `12 cm`, `yak. 5`). Bunları dosyada temizleyin.
- *Sayılar bin kat büyük ya da küçük.* Ondalık işareti ters okunmuş; sayfa hangisinin kullanıldığını gösterir. Sayıları binlik ayırıcı olmadan yazıp yeniden yükleyin.
- *Sütun adları ilk veri satırı ya da bir başlık.* Veri seti sayfasında **Başlık satırı**'nı ayarlayın.
- *Gün ile ay yer değiştirmiş.* Tarihler gün önce gelecek şekilde okunur. Belirsizlik kalmaması için dosyada `2021-04-03` biçiminde yazın.

## Model bağlamak

| İleti | Ne yapmalı |
|---|---|
| *No model is configured. Add one under Settings.* | Önce Ayarlar'ı doldurun. |
| *Endpoint returned 401: check your API key.* | Anahtar yanlış, iptal edilmiş ya da temel adresteki sağlayıcıdan başka birine ait. |
| *Endpoint returned 404: check the base URL and the model name.* | Temel adres (çoğu sağlayıcıda) `/v1` ile bitmeli, model adı da tam sağlayıcının yazdığı gibi olmalı. |
| *Endpoint returned 429: rate limited or out of credit.* | Bekleyin ya da sağlayıcıda bakiye ekleyin. Yeni bir hesapta çoğunlukla bakiye olmaz. |
| *The endpoint did not answer in time.* | Yeniden deneyin. Yerel bir model ilk çağrıda yükleniyordur. |
| *Could not resolve host …* / *Could not connect to the endpoint* | Temel adreste bir yazım hatası var ya da hizmet çalışmıyor. |
| *Base URL must use https://* | Düz `http://` yalnızca yerel uç noktalar için ve buna izin veren sunucularda kabul edilir. |
| *Host … resolves to a private or local address, which this server does not call.* | Bu sunucu yerel modellere izin vermiyor. Yerel model kullanmak için Chart-er'i kendiniz çalıştırın ([Modeller](models.md#kendi-bilgisayarınızda-bir-model)). |
| *This endpoint does not list its models. Type the model name.* | Hata değildir. Adı yazın. |

## Grafik yapmak

Bir revizyon **Başarısız** göründüğünde nedeni altında yazar; **İstek ve yanıt** sekmesi de modelin ne yanıt verdiğini gösterir.

| İleti | Ne anlama gelir, ne yapmalı |
|---|---|
| *The answer is not JSON.* / *The answer is not valid JSON* | Model iki kez düz yazı ya da bozuk JSON yazdı. Yeniden deneyin; sürerse başka bir model kullanın. |
| *The answer uses field names that are not in the profile* | Model sütun adı uydurdu. Yerel bir modelde bu hemen her zaman kesilmiş bir istektir: [Modeller](models.md#kendi-bilgisayarınızda-bir-model) sayfasındaki bağlam uzunluğuna bakın. Değilse yeniden deneyin ya da daha güçlü bir model kullanın. |
| *Not valid Vega-Lite v6 at …* | Model, belirtilen yerde hata içeren bir tanım yazdı. İsteği daha yalın yazın ya da modele daha az şey kalsın diye formda **Ne gösterilsin**'i seçin. |
| *The model hit its output limit before writing an answer.* | Akıl yürüten bir model bütün payını düşünmeye harcadı. Akıl yürütmeyen bir model kullanın ya da sağlayıcıda akıl yürütme ayarını düşürün. |
| *No row has … = …* | Süzgeç değeri o sütunda geçmiyor. Değeri listeden seçin; yazımı ve büyük-küçük harfleri kontrol edin. |
| *… holds numbers; … is not one.* | Süzgeç sütunu sayısal; bir sayı girin. |
| *… is a date column; filter on text or numbers.* | Formda tarihe göre süzme yoktur. |

**Grafik çizildi ama istediğiniz bu değil**

- *Ölçümleri topluyor.* **Ne gösterilsin** altında *Dağılım* ya da *Ortalama* seçin.
- *Belirttiğiniz bölümü değil, bütün veriyi gösteriyor.* **Yalnızca şu satırlar**'ı kullanın.
- *Dönemler yanlış sırada.* Sıra modelden değil, veri setinden gelir: bkz. [Dönem sütunları](periods.md#düzeltmek). Yeni sırayı alması için sonra grafiği revize edin.
- *Grafik boş.* **Veri** ve **Tanım** sekmelerinde hiçbir şeyle eşleşmeyen bir süzgeç arayın, sonra `süzgeci kaldır` diyerek revize edin.
- *Okunamayacak kadar çok çubuk ya da renk var.* Sütunda çok fazla farklı değer var. Bir alt kümeye süzün ya da daha kaba bir sütunu kullanın.
- *İstemediğiniz bir şeyi değiştirdi.* Grafiğin altındaki **Düzeltmeler**'i okuyun, sonra bir sonraki revizyonda neyin korunacağını söyleyin.

## Sınırlar

*Upload limit reached. Try again in an hour.* / *Revision limit reached. Try again in an hour.* Sınırlar hesap başına saatte 20 yükleme (örnek veri seti de bir yükleme sayılır) ve 60 revizyondur.

## Hâlâ çözülmediyse

Grafiğin **yeniden üretilebilirlik paketini** indirin (isteği, yanıtı ve nedeni içerir; satırlarınızı ve anahtarınızı içermez) ve Chart-er sunucunuzu işleten kişiye gönderin ya da <https://github.com/72perseid/charterv2/issues> adresinde bir kayda ekleyin. Önce, içindeki profilde paylaşamayacağınız bir şey bulunmadığını kontrol edin.
