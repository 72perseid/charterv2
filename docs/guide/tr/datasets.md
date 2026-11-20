# Veri setleri

Bir veri seti tek bir tablodur: ilk satırda sütun adları bulunur, diğer her satır bir kayıttır.

## Kabul edilen dosyalar

| | |
|---|---|
| Biçimler | `.csv`, `.tsv`, `.txt`, `.xlsx` |
| Desteklenmeyen | `.xls` (eski Excel). Dosyayı Excel ya da LibreOffice ile açıp `.xlsx` olarak kaydedin. |
| Boyut | en çok 20 MB, 100 000 satır, 200 sütun |
| Yükleme | hesap başına saatte 20 |

Özgün dosyanız değiştirilmeden saklanır ve veri seti sayfasından yeniden indirilebilir (**Özgün dosyayı indir**).

## Dosya nasıl okunur

Chart-er aşağıdakileri kendisi belirler ve her birini **Nasıl okundu** altında gösterir:

- **Kodlama.** Önce UTF-8, sonra Windows-1254 (Türkçe Excel dışa aktarımlarının olağan kodlaması), sonra Latin-1 denenir. Tabloda `ş`, `ğ` ya da `ı` bozuk görünüyorsa dosyayı UTF-8 olarak kaydedip yeniden yükleyin.
- **Ayırıcı.** Virgül, noktalı virgül, sekme ya da `|`; ilk satırlara hangisi uyuyorsa.
- **Ondalık işareti.** Noktalı virgülle ayrılmış bir dosyada, Türkçe ve Almanca Excel'in yazdığı gibi ondalık virgül (`12,5`) kullanıldığı varsayılır. Diğer durumlarda Chart-er hangi işaretle sayı sütunlarının okunabildiğine bakar. `1.250,50` gibi gruplanmış sayılar anlaşılır.
- **Tarihler** gün önce gelecek şekilde okunur: `03.04.2021`, 3 Nisan'dır.
- **Excel sayfası.** Boş olmayan ilk sayfa. Başka bir sayfayı **Sayfa** altından seçin.
- **Başlık satırı.** Excel'de, hücrelerinin en az yarısı dolu olan ilk satır; böylece tablonun üstündeki bir başlık atlanır. Sütun adları yine de yanlışsa **Başlık satırı**'nı kendiniz belirleyin. Sayım sıfırdan başlar: sayfanın ilk satırı 0'dır.

Hücrelerin başındaki ve sonundaki boşluklar atılır; `LN` ile `LN ` aynı değerdir.

## Sütun türleri

Her sütun tek bir tür alır. Tür, sütunun grafikte nasıl kullanılabileceğini belirler.

| Tür | Anlamı | Grafikte |
|---|---|---|
| tam sayı, sayı | tam ya da ondalıklı sayılar | ölçekli bir eksen; toplanabilir, ortalaması alınabilir |
| tarih | takvim tarihleri | zaman ekseni |
| metin | adlar, kategoriler, kodlar | her değer için bir çubuk, kutu ya da renk |
| mantıksal | evet / hayır | iki grup |
| dönem | arkeolojik dönemler | kronolojik sırayla gruplar; bkz. [Dönem sütunları](periods.md) |

*Metin* olarak okunan bir sayı sütununda hemen her zaman birkaç hücrede sayı olmayan bir şey vardır: `?`, `yak. 12`, `12 cm`, `-`. Bu hücreleri dosyada temizleyip yeniden yükleyin. Boş hücreler sorun değildir.

## Modelin gördüğü

Model dosyanızı hiçbir zaman almaz. Bir **profil** alır: sütunların bir tarifi. Profilin ne kadarını söyleyeceği her veri seti için **Modelin gördüğü** altından ayarlanır:

| Düzey | Modele gönderilen |
|---|---|
| **En az** | Sütun adları, türler, satır sayısı ve her sütunda kaç hücrenin boş, kaç değerin farklı olduğu. |
| **İstatistikler** (varsayılan) | En az düzeyine ek olarak sayı ve tarih sütunlarının en küçük ve en büyük değeri, ortalaması ve ortancası ile metin sütunlarının en sık beş değeri. |
| **Örnek** | İstatistiklere ek olarak tablodan on satır. Ham satırların sunucudan çıktığı tek düzey budur. |

Her düzeyde iki şey gönderilmez: her değeri farklı olan bir metin sütununun (buluntu numarası gibi bir kimlik) değerleri ve 40 karakterden uzun metin değerleri (kaynakçalar, notlar, bağlantılar).

Geçerli düzey, her grafik yaptığınızda istek kutusunun yanında gösterilir. *İstatistikler* hemen her grafik için yeterlidir. *En az*, kategori adlarının kendisi hassas olan veriler içindir; örneğin yayımlanmamış yerleşim adları. *En az* düzeyinde model bir sütunun hangi değerleri içerdiğini bilemez; bu yüzden grafiği tek bir değerle sınırlamak için cümleyi değil, formdaki **Yalnızca şu satırlar** denetimini kullanın.

Grafiğin kendisi, Chart-er sunucusunda duran satırlardan tarayıcınızda çizilir. Model tarifi yazar, sonucu hiç görmez.

## Silme

**Veri setini sil**; veri setini, sunucudaki dosyasını ve ondan yapılmış bütün grafikleri kaldırır. Bu işlem geri alınamaz.
