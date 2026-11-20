# Yeniden üretilebilirlik

Bir makaledeki grafik, onu üreten şeye kadar izlenebilmelidir. Arada bir dil modeli olduğunda bu kendiliğinden olmaz: aynı cümle yarın başka bir grafik verebilir. Chart-er'in buna yanıtı her şeyi kaydetmektir; böylece "bu şekil nasıl yapıldı?" sorusunun her zaman kesin bir yanıtı olur.

## Neler kaydedilir

Başarılı ya da başarısız, her revizyon için:

- modele gönderilen iletiler, sözcüğü sözcüğüne,
- modelin ham yanıtı, üzerinde hiçbir işlem yapılmadan önceki haliyle,
- denetimden sonraki tanım ve düzeltmelerin listesi,
- modelin adı, uç noktanın sunucu adı, sıcaklık ve tohum,
- Chart-er'in istem sürümü ve Chart-er'in kendi sürümü,
- kullanılan jetonlar, tahmini maliyet ve geçen süre.

Hepsi grafik sayfasında **İstek ve yanıt** altındadır.

## Paket

**Dışa aktar → Yeniden üretilebilirlik paketi**; grafiği, veri setinin profilini, dosyanın nasıl okunduğunu ve yukarıdaki kayıtla birlikte her revizyonu içeren tek bir JSON dosyası indirir.

Paket satırlarınızı içermez, API anahtarınızı da içermez. Ama modelin hangi düzeyi görmesine izin verilmiş olursa olsun, veri setinin bütün profilini içerir: sütun adları, aralıklar ve metin sütunlarının en sık değerleri. Yayımlamadan önce bunu kontrol edin.

Bir yayın için paket, veri setiyle birlikte bir şeklin eksiksiz kaynak kaydıdır. Yöntem bölümü için bir cümle:

> Şekil, Chart-er (sürüm `a3baa83`, istem `p2026-11-b`) ile, `<model>` modeli 0 sıcaklıkta kullanılarak üretilmiştir; istek, modelin yanıtı ve ortaya çıkan Vega-Lite tanımı `charter-chart-12.json` ek dosyasındadır.

Sürümler ve model adı pakette ve grafik sayfasında yazar.

## Bir grafiği yeniden çalıştırmak

Elinde bir paket ve bir anahtar olan herkes kayıtlı isteği yeniden gönderip yanıtı karşılaştırabilir. Bunun için Chart-er'in bir kopyası gerekir; hesap ve veritabanı gerekmez:

```sh
docker compose -f deploy/compose.yml run --rm -T api \
  python manage.py replay /tmp/charter-chart-12.json --revision 2 \
  --base-url https://api.openai.com/v1 --model gpt-4.1-mini --api-key sk-...
```

`--revision` verilmezse son revizyon, `--model` verilmezse paketteki model kullanılır; `--out` yeniden üretilen tanımı bir dosyaya yazar. Komut kayıtlı iletileri kayıtlı parametrelerle gönderir, yanıtı sunucunun yaptığı gibi denetler ve tanımın aynı olup olmadığını ya da nerede ayrıştığını bildirir.

## Bunun vaat ettiği ve etmediği

Hiçbir sağlayıcı, 0 sıcaklıkta ve sabit tohumla bile aynı yanıtı iki kez vermeyi garanti etmez; modeller de kullanımdan kaldırılır. Gelecek yıl yapılan bir yeniden çalıştırma farklı sonuç verebilir ya da hiç yapılamayabilir.

Garanti edilen şey kayıttır: yayımladığınız grafik bu tanımdan gelmiştir; tanım pakettedir ve her zaman aynı grafiği çizer; tanım da bu modele yapılan bu istekten gelmiştir. Yeniden üretilebilir olan nesne tanımdır; model çağrısı onun belgelenmiş kökenidir.
