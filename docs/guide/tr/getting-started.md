# Başlarken

Chart-er bir tabloyu ve bir cümleyi grafiğe çevirir. Bir CSV ya da Excel dosyası yüklersiniz, sütunları seçersiniz, ne görmek istediğinizi yazarsınız ve bir dil modeli grafiği yazar. Bu sayfa sizi yaklaşık beş dakikada sıfırdan ilk grafiğe götürür.

İki şeye ihtiyacınız var: bir Chart-er sunucusunda hesap ve bir dil modeline erişim. Model sizindir: Chart-er bir modelle birlikte gelmez ve modelin ücretini ödemez. Önce yalnızca etrafa bakmak isterseniz 1. ve 2. adımlar için model gerekmez.

## 1. Hesap oluşturun

Siteyi açın ve **Hesap oluştur**'u seçin. Bir e-posta adresi ve en az sekiz karakterli bir parola girin. Ad isteğe bağlıdır ve yalnızca üst çubukta görünür.

Dil seçimi (English / Türkçe) üst çubuktadır. Chart-er tarayıcınızın diliyle açılır.

## 2. Bir veri seti ekleyin

**Veri setleri** sayfasında:

- **Yükle**'ye basıp en çok 20 MB büyüklüğünde bir `.csv`, `.tsv`, `.txt` ya da `.xlsx` dosyası seçin, ya da
- **Örneği dene**'ye basın. Bu, küçük bir buluntu tablosu ekler (kova no, açma, dönem, buluntu türü, malzeme, adet, ağırlık). Satırlar uydurmadır; kendi dosyanız olmadan her adımı deneyebilmeniz için vardır.

Veri seti önce *Bekliyor*, kısa süre sonra *Tamam* durumuna geçer. Sayfa o zaman dosyanın nasıl okunduğunu ve her sütun için bir satır gösterir: türü, kaç hücrenin boş olduğu, kaç farklı değer içerdiği ve bir özet. Burada bir şey yanlış görünüyorsa (metin olarak okunmuş bir sayı sütunu, aslında başlık satırı olan sütun adları) grafik yapmadan önce düzeltin: bkz. [Veri setleri](datasets.md).

## 3. Bir model bağlayın

**Ayarlar**'ı açın ve şunları girin:

- OpenAI uyumlu bir hizmetin **temel adresi**, örneğin `https://api.openai.com/v1` ya da `https://openrouter.ai/api/v1`,
- o hizmetteki **API anahtarınız**,
- sonra **Modelleri getir**'e basıp birini seçin.

**Kaydet**'e, ardından **Bağlantıyı sına**'ya basın. Yeşil *Bağlandı* yazısı hazır olduğunuzu gösterir. [Modeller](models.md) sayfası seçenekleri anlatır; bunların arasında, hiçbir şeyin bilgisayarınızdan çıkmaması için kendi bilgisayarınızda çalışan bir model de vardır.

## 4. Bir grafik yapın

Veri setini açın ve **Yeni grafik** bölümüne inin.

1. **X ekseni** ve **Y ekseni** sütunlarını seçin. Örnek veri setiyle: X = `Dönem`, Y = `Adet`.
2. İsterseniz grafiği gruplara ayırmak için bir **Renk** sütunu seçin, örneğin `Malzeme`.
3. **Ne gösterilsin** altında *Model karar versin*'i bırakın ya da kendiniz belirleyin. Sayımlar için *Toplam*'ı, uzunluk gibi ölçümler için *Dağılım* ya da *Ortalama*'yı seçin.
4. **Grafiği** bir cümleyle **tarif edin**: `Dönemlere göre toplam buluntu, çubuk grafik`.
5. **Grafik oluştur**'a basın.

Grafik sayfası açılır ve modeli bekler; bu çoğunlukla birkaç saniye sürer. Sonra grafik görünür. Örnek veri setinde x eksenindeki dönemler alfabetik değil, eskiden yeniye doğru sıralanır: Chart-er sütunun dönem içerdiğini tanımış ve sırayı kendisi vermiştir.

## 5. Değiştirin

**Revize et** altında neyin değişeceğini yazın (`yatay yap`, `malzemeye göre renklendir`, `yalnızca A açmasını göster`) ve **Revizyon oluştur**'a basın. Her revizyon saklanır; yandaki listeden istediğinize geri dönebilirsiniz.

**Dışa aktar** altından grafiği PNG ya da SVG olarak kaydedebilirsiniz.

## Sonra nereye

- Dosyanız beklediğiniz gibi okunmadıysa: [Veri setleri](datasets.md)
- Dönemler yanlış sıradaysa: [Dönem sütunları](periods.md)
- Grafik istediğiniz gibi değilse: [Grafikler](charts.md)
- Kırmızı bir ileti görüyorsanız: [Sorun giderme](troubleshooting.md)
