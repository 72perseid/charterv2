import type { Strings } from './en';

export const tr: Strings = {
  appName: 'Chart-er',
  nav: { datasets: 'Veri setleri', charts: 'Grafikler', settings: 'Ayarlar', help: 'Yardım', signOut: 'Çıkış' },
  language: { label: 'Dil', en: 'English', tr: 'Türkçe' },
  landing: {
    title: 'Chart-er',
    lead: 'Bir tablo ve bir cümle girer. Bir Vega-Lite grafiği ve nasıl üretildiğinin tam kaydı çıkar.',
    what: [
      'Bir CSV ya da Excel dosyası yükleyin. Chart-er dosyanın profilini çıkarır: sütun adları, çıkarsanan türler, temel istatistikler.',
      'Sütunları seçin, grafiği kendi cümlelerinizle tarif edin; seçtiğiniz dil modeli Vega-Lite tanımını yazsın.',
      'Her revizyon, onu üreten isteğin birebir kaydıyla saklanır; böylece her grafik girdilerine kadar izlenebilir.'
    ],
    dataFlow:
      'Bu sunucudan yalnızca veri seti profili çıkar; o da yalnızca kendi anahtarınızla tanımladığınız model uç noktasına gider. Ham satırlar, veri setini örnek moduna almadığınız sürece asla gönderilmez.',
    signIn: 'Giriş yap',
    register: 'Hesap oluştur',
    source: 'Kaynak kodu',
    help: 'Nasıl çalışır'
  },
  auth: {
    signIn: 'Giriş yap',
    register: 'Hesap oluştur',
    email: 'E-posta',
    password: 'Parola',
    displayName: 'Ad (isteğe bağlı)',
    noAccount: 'Hesabınız yok mu?',
    haveAccount: 'Zaten hesabınız var mı?',
    working: 'Bekleyin…'
  },
  datasets: {
    title: 'Veri setleri',
    upload: 'Yükle',
    empty:
      'Henüz veri seti yok. Başlamak için bir CSV ya da Excel dosyası yükleyin ya da örneği deneyin.',
    example: 'Örneği dene',
    exampleTitle:
      'Veri setlerinize dönemlere göre buluntuları içeren küçük bir tablo ekler. Satırlar uydurmadır. İncelemek için model ya da anahtar gerekmez.',
    exampleAdding: 'Ekleniyor…',
    columns: { name: 'Ad', rows: 'Satır', columns: 'Sütun', status: 'Durum', created: 'Oluşturulma' },
    uploadForm: {
      title: 'Veri seti yükle',
      file: 'Dosya (.csv, .tsv, .txt ya da .xlsx, en çok 20 MB)',
      name: 'Ad',
      submit: 'Yükle',
      cancel: 'Vazgeç',
      uploading: 'Yükleniyor…'
    },
    detail: {
      parsing: 'Dosya okunuyor. Bu sayfa kendiliğinden güncellenir.',
      failed: 'Okuma başarısız',
      file: 'Dosya',
      download: 'Özgün dosyayı indir',
      delete: 'Veri setini sil',
      confirmDelete: 'Kalıcı olarak silinsin mi?',
      newChart: 'Yeni grafik',
      profile: 'Sütunlar',
      rows: 'İlk satırlar',
      rowsOf: '/',
      parse: 'Nasıl okundu',
      encoding: 'Kodlama',
      delimiter: 'Ayırıcı',
      decimal: 'Ondalık işareti',
      sheet: 'Sayfa',
      headerRow: 'Başlık satırı',
      headerRowHint: 'Sıfırdan başlayan satır numarası. Sütun adları yanlış görünüyorsa değiştirin.',
      apply: 'Uygula',
      profileColumns: {
        name: 'Sütun',
        original: 'Özgün ad',
        type: 'Tür',
        nulls: 'Boş',
        distinct: 'Farklı',
        summary: 'Özet'
      },
      period: {
        unplaced: 'yerleştirilemedi, sonda sıralanır',
        yours: 'sizin sıranız',
        edit: 'Sıra ve kaynaklar',
        treat: 'Dönem olarak işle',
        dates: 'Tarihleri sütunlardan al',
        datesTitle: 'Değerleri tarihlenecek sütun:',
        datesHint:
          'Bu veri setinde her satırın başlangıç ve bitiş yılını tutan sütunları seçin. Her değer, satırlarındaki en erken başlangıca ve en geç bitişe göre yerleştirilir ve bu tarihler PeriodO\'dan önce gelir. Satırlarında tarih olmayan değerler yine PeriodO\'da aranır.',
        datesStart: 'Başlangıç yılı sütunu',
        datesEnd: 'Bitiş yılı sütunu',
        datesNone: '(yok)',
        datesBc: 'Yıllar MÖ sayılıyor (1500, MÖ 1500 demek)',
        datesSave: 'Bu tarihleri kullan',
        datesRemove: 'Bağlantıyı kaldır',
        datedBy: 'Tarihlendiren sütunlar',
        varies: 'tarihler satırdan satıra değişiyor; en geniş aralık kullanıldı',
        placedBy: 'Her değer nasıl yerleştirildi',
        datedFor: 'Tarihlendirme bölgesi',
        snapshot: 'PeriodO kopyası',
        bc: 'MÖ',
        ad: 'MS',
        via: {
          periodo: 'PeriodO',
          abbreviation: 'PeriodO, kısaltma açıldı',
          translation: 'PeriodO, çevrildi',
          derived: 'bir PeriodO döneminin parçası',
          year: 'etiketteki tarih',
          model: 'modeliniz',
          user: 'sizin anlamınız',
          data: 'bu veri setindeki tarihler'
        },
        means: 'Anlamı',
        meansPlaceholder: 'örn. Late Neolithic ya da MÖ 5300-4500',
        meansHint:
          'Bir değerin ne anlama geldiğini yazın: yaygın yazılışıyla bir dönem adı ya da bir tarih. Diğer etiketler gibi PeriodO\'da aranır ve bulunan eşleşmenin yerine geçer.',
        notRead: 'okunamadı',
        notPlaced: 'yerleştirilemedi',
        saveMappings: 'Anlamları kaydet',
        typeOrder: 'Ya da bütün sırayı elle yazın',
        modelEstimate: 'tahmin, PeriodO tanımı yok',
        ask: 'Yerleştirilemeyen değerleri modele sor',
        askConfirm: 'Bu sütunun değerleri modelinize gönderilsin mi?',
        askHint:
          'Yalnızca bu sütunun farklı değerlerini Ayarlar\'daki model uç noktasına gönderir. Bu düğmeye basmadıkça hiçbir şey gönderilmez.',
        askFailed: 'Modele sorulamadı',
        editorLabel: 'Kronolojik sıra:',
        editorHint: 'Her satıra bir değer, en eski en üstte. Yazmadığınız değerler sonda sıralanır.',
        save: 'Sırayı kaydet',
        detect: 'Yeniden algıla',
        notPeriod: 'Dönem değil',
        cancel: 'Kapat'
      }
    },
    privacy: {
      label: 'Modelin gördüğü',
      levels: {
        minimal: 'En az',
        statistics: 'İstatistikler',
        sample: 'Örnek'
      },
      describe: {
        minimal: 'Sütun adları, türler, satır sayısı, boş ve farklı değer sayıları.',
        statistics: 'En az düzeyine ek olarak sayısal ve tarih aralıkları ile en sık kategorik değerler.',
        sample: 'İstatistiklere ek olarak sabit tohumla seçilmiş on satır. Ham değerler sunucudan çıkar.'
      }
    }
  },
  types: {
    integer: 'tam sayı',
    number: 'sayı',
    date: 'tarih',
    boolean: 'mantıksal',
    string: 'metin',
    period: 'dönem'
  },
  charts: {
    title: 'Grafikler',
    empty: 'Henüz grafik yok. Bir veri seti açın ve istediğiniz grafiği tarif edin.',
    columns: { title: 'Başlık', dataset: 'Veri seti', status: 'Durum', revisions: 'Revizyon', updated: 'Güncelleme' },
    form: {
      title: 'Yeni grafik',
      chartTitle: 'Başlık (isteğe bağlı)',
      x: 'X ekseni',
      y: 'Y ekseni',
      color: 'Renk (isteğe bağlı)',
      none: '— yok —',
      show: 'Ne gösterilsin',
      shows: {
        auto: 'Model karar versin',
        total: 'Toplam',
        average: 'Ortalama',
        count: 'Satır sayısı',
        distribution: 'Dağılım (kutu grafiği)',
        points: 'Her satır bir nokta'
      },
      showHint:
        'Burada seçtiğiniz, model ne yanıt verirse versin grafiğe uygulanır. Uzunluk gibi ölçümler toplam değil, dağılım ya da ortalama olarak gösterilir.',
      filterField: 'Yalnızca şu satırlar (isteğe bağlı)',
      filterAll: '— tüm satırlar —',
      filterValue: 'eşittir',
      prompt: 'Grafiği tarif edin',
      promptHint: 'Örneğin: açmalara göre toplam buluntu sayısı çubuk olarak, ya da ağırlığın zamana göre değişimi çizgi olarak.',
      privacyNote: 'Modelin göreceği: {level}',
      create: 'Grafik oluştur',
      creating: 'Oluşturuluyor…'
    },
    page: {
      dataset: 'Veri seti',
      revision: 'Revizyon',
      waiting: 'Model bekleniyor.',
      running: 'Model tanımı yazıyor.',
      failed: 'Üretim başarısız',
      tabs: { chart: 'Grafik', data: 'Veri', spec: 'Tanım', request: 'İstek ve yanıt' },
      revisions: 'Revizyonlar',
      current: 'geçerli',
      makeCurrent: 'Bunu geçerli revizyon yap',
      revise: {
        title: 'Revize et',
        lead: 'Revizyon {n} temel alınır. Alanları ya da isteği değiştirin; model önceki tanımı da görür.',
        prompt: 'Ne değişsin?',
        submit: 'Revizyon oluştur',
        creating: 'Oluşturuluyor…'
      },
      export: {
        title: 'Dışa aktar',
        png: 'PNG',
        svg: 'SVG',
        json: 'Tanım JSON',
        bundle: 'Yeniden üretilebilirlik paketi',
        bundleHint: 'Veri seti profilini, nasıl okunduğunu ve her revizyonu isteği ve yanıtıyla içeren tek bir JSON dosyası.'
      },
      dataRows: '{total} satırın {shown} tanesi',
      corrections: 'Modelin yanıtına uygulanan düzeltmeler',
      adjustments: 'Bu uç nokta için uyarlanan parametreler',
      record: {
        model: 'Model',
        endpoint: 'Uç nokta',
        temperature: 'Sıcaklık',
        seed: 'Tohum',
        promptVersion: 'İstem sürümü',
        appVersion: 'Uygulama sürümü',
        duration: 'Süre',
        tokens: 'Jeton',
        tokensDetail: '{prompt} giriş, {completion} çıkış{reasoning}',
        reasoning: ' ({n} tanesi akıl yürütme)',
        cost: 'Tahmini maliyet',
        costAtCurrent: 'güncel fiyatlarla; bu grafik fiyatlar girilmeden önce üretildi',
        costUnknown: 'fiyatları Ayarlar altında girin',
        attempt: 'Deneme'
      },
      messages: 'Gönderilen iletiler',
      response: 'Ham yanıt',
      delete: 'Grafiği sil',
      confirmDelete: 'Kalıcı olarak silinsin mi?'
    }
  },
  settings: {
    title: 'Ayarlar',
    model: {
      title: 'Model',
      lead: 'Chart-er veri seti profilini, sizin seçtiğiniz ve ücretini sizin ödediğiniz OpenAI uyumlu bir sohbet uç noktasına gönderir. Anahtar bu sunucuda şifreli saklanır; şifreleme anahtarı işletmecidedir.',
      baseUrl: 'Temel adres',
      baseUrlHint: '/v1 dahil olmak üzere adres. Örneğin https://api.openai.com/v1, https://openrouter.ai/api/v1 ya da https://api.anthropic.com/v1.',
      model: 'Model',
      modelHint: 'Sağlayıcının döndürdüğü listeden seçin ya da bir ad yazın.',
      loadModels: 'Modelleri getir',
      loadingModels: 'Getiriliyor…',
      modelsLoaded: 'Bu uç noktadan {n} model.',
      modelsNeedKey: 'Model listesini getirmek için temel adresi ve bir API anahtarı girin.',
      modelsNeedUrl: 'Model listesini getirmek için temel adresi girin.',
      otherModel: 'Diğer (ad yazın)',
      apiKey: 'API anahtarı',
      apiKeyKeep: '{hint} ile biten bir anahtar kayıtlı. Korumak için boş bırakın.',
      apiKeyNew: 'Bir kez yapıştırılır, bir daha gösterilmez.',
      apiKeyOptional: 'Bir kez yapıştırılır, bir daha gösterilmez. Ollama gibi anahtar denetlemeyen yerel bir model için boş bırakın.',
      temperature: 'Sıcaklık',
      temperatureHint: '0 en tekrarlanabilir grafikleri verir.',
      prices: 'Fiyatlar (milyon jeton başına USD)',
      inputPrice: 'Giriş',
      outputPrice: 'Çıkış',
      pricesHint: 'Yalnızca her grafiğin maliyetini tahmin etmek için kullanılır. Bilmiyorsanız boş bırakın.',
      pricesFromProvider: 'Sağlayıcının bu model için yayımladığı fiyatlardan dolduruldu.',
      save: 'Kaydet',
      saved: 'Kaydedildi.',
      test: 'Bağlantıyı sına',
      testing: 'Sınanıyor…',
      connected: 'Bağlandı',
      notConnected: 'Bağlanamadı',
      unsaved: 'Önce yapılandırmayı kaydedin, sonra sınayın.'
    },
    account: {
      title: 'Hesap',
      email: 'E-posta',
      name: 'Ad',
      signOut: 'Çıkış'
    }
  },
  help: {
    title: 'Yardım',
    lead: 'Bir tablodan grafiğe nasıl gidilir ve Chart-er bu yolda neler yapar.',
    contents: 'Bu sayfada',
    sections: [
      {
        id: 'start',
        title: 'Beş adımda',
        paragraphs: [],
        points: [
          'Veri setleri: bir CSV ya da Excel dosyası yükleyin ya da "Örneği dene" ile uydurma satırlardan oluşan küçük bir buluntu tablosu ekleyin.',
          'Sütun tablosuna bakın. Sayıların sayı olarak okunduğunu ve sütun adlarının doğru olduğunu kontrol edin.',
          'Ayarlar: bir dil modelinin adresini ve anahtarını girin, model listesini getirin, kaydedin ve bağlantıyı sınayın.',
          'Veri setini açın, X ve Y sütunlarını seçin, ne görmek istediğinizi yazın ve grafiği oluşturun.',
          'Doğru olana kadar bir cümleyle revize edin ("yatay yap"), sonra PNG ya da SVG olarak dışa aktarın.'
        ]
      },
      {
        id: 'files',
        title: 'Dosyanız',
        paragraphs: [
          'Her dosyada tek tablo: ilk satırda sütun adları, her satırda bir kayıt. CSV, TSV ve xlsx kabul edilir; en çok 20 MB, 100 000 satır ve 200 sütun. Eski .xls dosyalarını önce .xlsx olarak kaydedin.',
          'Chart-er kodlamayı, ayırıcıyı, ondalık işaretini, sayfayı ve başlık satırını kendisi belirler ve her birini "Nasıl okundu" altında gösterir. Türkçe Excel\'in yazdığı noktalı virgüllü, ondalık virgüllü dosyalar doğru okunur. Tarihler gün önce gelecek şekilde okunur.'
        ],
        points: [
          '"Metin" görünen bir sayı sütununda sayı olmayan hücreler vardır ("?", "12 cm"). Bunları dosyada temizleyip yeniden yükleyin.',
          'Sütun adları aslında bir başlık ya da veri satırıysa veri seti sayfasında "Başlık satırı"nı değiştirin. Sayım 0\'dan başlar.',
          'Türkçe harfler bozuk çıkıyorsa dosyayı UTF-8 olarak kaydedin.'
        ]
      },
      {
        id: 'periods',
        title: 'Dönem sütunları',
        paragraphs: [
          'Arkeolojik dönemler içeren bir sütun ("Geç Tunç Çağı", "Helenistik", "EB II", "MÖ 5. yüzyıl", "1500 BC") "dönem" türünü alır ve onu kullanan her grafik alfabetik değil, eskiden yeniye doğru sıralanır. Adlar, yayımlanmış dönem tanımlarının dizini olan PeriodO\'dan, sütununuzun işaret ettiği bölgeye göre tarihlenir.',
          'Her değere hangi yılların verildiğini ve bunların hangi yayından geldiğini görmek için sütunda "Sıra ve kaynaklar"a basın. Bir grafiği sunmadan önce burayı kontrol edin. Düzeltmeler de buradan yapılır:'
        ],
        points: [
          'Bir değerin anlamını yazın: "ECh", "Early Chalcolithic" demektir; "Evre 7", "720-650 BC" demektir.',
          '"Tarihleri sütunlardan al": kendi tablonuzdaki başlangıç ve bitiş yılı sütunlarını kullanın.',
          'Bütün sırayı elle yazın, her satıra bir değer. Tek bir yerleşimin evreleri için en uygun yol budur.',
          'Yerleştirilemeyen değerleri modelinize sorun. Sütunun değerlerini modele yalnızca bu düğme gönderir ve önce onayınızı ister.',
          '"Dönem değil" özelliği kapatır; "Dönem olarak işle" tanınmamış bir sütun için açar.'
        ]
      },
      {
        id: 'model',
        title: 'Model',
        paragraphs: [
          'Chart-er\'in kendi dil modeli yoktur. Ayarlar\'da kendi anahtarınızla bir model bağlarsınız ve kullandığınız kadarını sağlayıcınıza ödersiniz: küçük bir modelde grafik başına bir sentin çok altında. Sohbet aboneliği API anahtarı içermez; anahtarı sağlayıcının geliştirici sayfalarından alırsınız.',
          'Temel adres, sağlayıcının /v1 ile biten adresidir; örneğin https://api.openai.com/v1 ya da https://openrouter.ai/api/v1. Küçük ve ucuz bir model yeterlidir. En tekrarlanabilir grafikler için sıcaklığı 0\'da bırakın.',
          'Anahtarınız şifrelenerek saklanır ve yalnızca girdiğiniz adresi çağırmak için kullanılır. Bu sunucuyu işleten kişi şifreyi çözebilir; bu yüzden harcama sınırı olan bir anahtar kullanın.'
        ],
        points: []
      },
      {
        id: 'chart',
        title: 'Grafiği tarif etmek',
        paragraphs: [
          'Sütunları seçin, sonra ne istediğinizi bir meslektaşınıza söyler gibi, Türkçe ya da İngilizce yazın: "Dönemlere göre toplam buluntu, çubuk grafik", "Açmalara göre ağırlık, mal grubuna göre renkli". Grafik türü sizin için önemliyse adını yazın. Her istekte tek grafik: yan yana paneller ve katmanlı grafikler desteklenmez.',
          'İki seçim, modelin cümlenizi nasıl okuduğuna bağlı kalmasın diye formda yapılabilir. Model ne yanıt verirse versin, Chart-er bunları grafiğe kendisi uygular.'
        ],
        points: [
          '"Ne gösterilsin". Toplam: sayım ve ağırlık gibi toplanabilen miktarlar için. Ortalama: her grup için tipik bir değer. Satır sayısı: her grupta kaç kayıt olduğu. Dağılım: uzunluk gibi ölçümler için kutu grafiği. Her satır bir nokta: ham değerler.',
          'Ölçümleri toplamayın. Kırk kemik uzunluğunun toplamı bir şey ifade etmez; Dağılım ya da Ortalama seçin.',
          '"Yalnızca şu satırlar … eşittir …" grafiği bir sütunun tek bir değeriyle sınırlar; örneğin Bölge eşittir Teselya. Hiçbir satırda bulunmayan bir değer hemen reddedilir.'
        ]
      },
      {
        id: 'result',
        title: 'Sonucu okumak',
        paragraphs: [
          'Grafik sayfasında dört sekme vardır: grafik, arkasındaki satırlar, Vega-Lite tanımı ve modele giden istek ile gelen yanıtın birebir kaydı; model, jeton sayıları ve tahmini maliyetle birlikte.',
          'Chart-er modelin yanıtını denetler ve yaptığı her değişikliği "Modelin yanıtına uygulanan düzeltmeler" altında listeler: sıraya konan bir dönem sütunu, yanlış yazılmış bir sütun adının değiştirilmesi, toplama biçiminin sizin seçiminize çevrilmesi. Bir grafik sizi şaşırtırsa önce bu listeyi okuyun. Sütunlarınızla hiç ilgisi olmayan bir yanıt onarılmaz, gerekçesiyle reddedilir.'
        ],
        points: []
      },
      {
        id: 'revise',
        title: 'Revizyonlar ve dışa aktarma',
        paragraphs: [
          'Her değişiklik yeni bir revizyondur; hiçbir şeyin üzerine yazılmaz. Model önceki tanımı da görür; bu yüzden "logaritmik ölçek kullan" yalnızca onu değiştirir. Listeden bir revizyona tıklayarak ona bakabilir, ondan yeni bir revizyon başlatabilir ya da onu geçerli revizyon yapabilirsiniz.',
          'Sunumlar için PNG, baskı için SVG ya da tanımı JSON olarak dışa aktarın. Yeniden üretilebilirlik paketi, veri seti profilini ve her revizyonun isteğini, yanıtını ve tanımını içeren tek bir dosyadır. Satırlarınızı da anahtarınızı da içermez; yayımlanan bir şeklin yanında saklanacak dosya budur.'
        ],
        points: []
      },
      {
        id: 'privacy',
        title: 'Bu sunucudan ne çıkar',
        paragraphs: [
          'Model dosyanızı hiçbir zaman almaz. Veri setinin bir profilini alır; o da yalnızca Ayarlar\'da girdiğiniz adrese gider. Profilin ne kadarını söyleyeceğini her veri seti için "Modelin gördüğü" altında siz belirlersiniz:'
        ],
        points: [
          'En az: sütun adları, türler, satır sayısı, boş ve farklı değer sayıları.',
          'İstatistikler (varsayılan): ayrıca sayı ve tarih sütunlarının aralıkları ile metin sütunlarının en sık beş değeri.',
          'Örnek: ayrıca tablodan on satır. Ham satırların gönderildiği tek düzey budur.',
          'Her düzeyde, kimlik sütunlarının değerleri gönderilmez ve 40 karakterden uzun metin değerleri dışarıda bırakılır.'
        ]
      },
      {
        id: 'problems',
        title: 'Bir şey başarısız olduğunda',
        paragraphs: ['Başarısız bir revizyon nedenini söyler; "İstek ve yanıt" sekmesi modelin ne yanıt verdiğini gösterir. Hata iletileri İngilizcedir.'],
        points: [
          '"Endpoint returned 401": anahtar yanlış ya da başka bir sağlayıcıya ait. "404": temel adresi (çoğunlukla /v1 ile biter) ve model adını kontrol edin. "429": istek sınırına takıldınız ya da hesapta bakiye yok.',
          '"The endpoint did not answer in time": yeniden deneyin. Kendi bilgisayarınızdaki bir model ilk çağrıda henüz yükleniyordur.',
          '"The answer is not JSON" ya da "Not valid Vega-Lite": model iki kez hata yaptı. Yeniden deneyin, isteği sadeleştirin, formda "Ne gösterilsin"i seçin ya da başka bir model kullanın.',
          '"The answer uses field names that are not in the profile": model sütun uydurdu. Yerel bir modelde istek büyük olasılıkla kesilmiştir; bağlam uzunluğunu artırın (Ollama için OLLAMA_CONTEXT_LENGTH=16384).',
          'Grafik ölçümleri topluyorsa Dağılım ya da Ortalama seçin. Bütün veriyi gösteriyorsa "Yalnızca şu satırlar"ı kullanın. Dönemler sırasızsa veri seti sayfasında düzeltin, sonra grafiği revize edin.',
          'Sınırlar: saatte 20 yükleme ve 60 revizyon.'
        ]
      }
    ]
  },
  status: { pending: 'Bekliyor', running: 'Çalışıyor', done: 'Tamam', failed: 'Başarısız' },
  errors: {
    network: 'Sunucuya ulaşılamadı.',
    unknown: 'Bir şeyler ters gitti.'
  }
};
