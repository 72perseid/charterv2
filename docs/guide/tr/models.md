# Modeller

Chart-er bir dil modeli içermez. Modeli **Ayarlar** altından siz bağlarsınız: bir sağlayıcıdaki kendi hesabınızla ya da kendi bilgisayarınızda çalışan bir modelle. Bu bilinçli bir tercihtir: verinizin tarifinin nereye gideceğine siz karar verirsiniz ve tam kullandığınız kadarını ödersiniz.

Bir grafik çok az tutar. Bir istek yaklaşık 1 000 ile 3 000 jeton giriş ve birkaç yüz jeton çıkıştır; küçük bir barındırılan modelde bir sentin çok altındadır.

## Barındırılan bir model bağlamak

1. Bir sağlayıcıdan API anahtarı alın. Bu, sohbet aboneliğinden ayrıdır: ChatGPT ya da Claude aboneliği API anahtarı içermez.
2. **Ayarlar**'da **temel adresi** girin: sağlayıcının `/v1` ile biten adresi.

   | Sağlayıcı | Temel adres |
   |---|---|
   | OpenAI | `https://api.openai.com/v1` |
   | OpenRouter (tek anahtarla birçok model) | `https://openrouter.ai/api/v1` |
   | Anthropic | `https://api.anthropic.com/v1` |

   OpenAI sohbet biçimini konuşan her hizmet aynı şekilde çalışır.
3. **API anahtarını** yapıştırın. Bir kez gösterilir, bir daha gösterilmez; sonrasında sayfa yalnızca hangi anahtarın saklandığını son karakterleriyle belirtir.
4. **Modelleri getir**'e basıp birini seçin. Sağlayıcı liste yayımlamıyorsa modelin adını yazın.
5. **Kaydet**'e, sonra **Bağlantıyı sına**'ya basın. Sınama tek bir küçük ileti gönderir ve ne döndüğünü bildirir.

## Hangi model

Küçük ve ucuz bir model yeterlidir: bir grafik tanımı yazmak zor bir iş değildir. Önemli olan, modelin temiz JSON ile yanıt vermesi ve kendisine verilen sütun adlarına bağlı kalmasıdır. Büyük sağlayıcıların güncel küçük modelleri bunu yapar. Akıl yürüten modeller de çalışır ama daha yavaştır ve burada görünür bir kazanç sağlamadan daha pahalıya gelir.

## Sıcaklık ve fiyatlar

**Sıcaklık**, siz değiştirmedikçe 0'dır. 0 en tekrarlanabilir sonucu verir: aynı istek çoğunlukla aynı grafiği üretir. Bazı modeller sıcaklık değerini reddeder; Chart-er o zaman bu değeri göndermez ve bunu grafikte belirtir.

**Fiyatlar** yalnızca her grafiğin ne kadar tuttuğunu göstermek için kullanılır. Sağlayıcı yayımlıyorsa kendiliğinden dolar (OpenRouter yayımlar). Aksi halde sağlayıcının fiyat listesinden milyon jeton başına giriş ve çıkış fiyatını girin ya da boş bırakın; o zaman maliyet bilinmiyor olarak görünür.

## Kendi bilgisayarınızda bir model

Yerel bir model sunucusuyla makinenizden hiçbir şey çıkmaz. [Ollama](https://ollama.com), LM Studio, llama.cpp ve vLLM'in hepsi çalışır.

Bunun için Chart-er'in aynı makinede ya da aynı ağda çalışması ve onu işleten kişinin yerel uç noktalara izin vermiş olması gerekir. Herkese açık bir Chart-er sunucusu özel ağlardaki adresleri reddeder. Kurulum [README](../../../README.md#running-with-a-local-model) dosyasında anlatılır. Kurulduktan sonra:

- Temel adres: Chart-er Docker içinde çalışıyorsa Ollama için `http://host.docker.internal:11434/v1`.
- API anahtarı: boş bırakın.
- Model: listeyi getirin ve bilgisayarınızın belleğine sığan birini seçin. 8 GB'lık bir ekran kartında `qwen2.5:7b` gibi 7B'lik bir model birkaç saniyede yanıt verir.

Yerel modellerle ilgili bilinmesi gereken iki şey:

- **İlk istek yavaştır.** Modelin belleğe yüklenmesi gerekir. Bağlantı sınaması uç noktanın zamanında yanıt vermediğini söylerse yeniden çalıştırın.
- **Bağlam uzunluğunu kontrol edin.** Ollama, aksi söylenmedikçe bir isteğin yalnızca ilk 4 096 jetonunu okur ve isteği kestiğinde bir şey demez. Model o zaman hiç görmediği sütunlar hakkında yanıt verir ve Chart-er yanıtı reddeder. Geniş tablolar için Ollama'nın çalıştığı yerde `OLLAMA_CONTEXT_LENGTH=16384` ayarını yapın.

Küçük yerel modeller barındırılanlardan daha çok hata yapar. Chart-er her yanıtı denetler, güvenle onarabildiğini onarır, yanıt geçersizse bir kez daha sorar ve vazgeçtiğinde nedenini söyler. Grafik formundaki seçimler (**Ne gösterilsin**, **Yalnızca şu satırlar**) en çok küçük modellerde işe yarar; çünkü modelin cümlenizi nasıl okuduğuna bağlı değildirler.

## Anahtarınız

Anahtar Chart-er sunucusunda şifrelenerek saklanır ve yalnızca girdiğiniz uç noktayı çağırmak için kullanılır. Sunucuyu işleten kişi şifreleme anahtarını elinde tutar ve ilke olarak sizinkini çözebilir. Kendinizin işletmediği bir sunucuda harcama sınırı olan bir anahtar kullanın ve artık gerekmediğinde anahtarı sağlayıcıda iptal edin.
