import type { Strings } from './en';

export const tr: Strings = {
  appName: 'Chart-er',
  nav: { datasets: 'Veri setleri', charts: 'Grafikler', settings: 'Ayarlar', docs: 'Belgeler', signOut: 'Çıkış' },
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
    docs: 'Belgeler'
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
      choose: '— bir sütun seçin —',
      noModel: 'Henüz bir model bağlı değil; bu yüzden grafik yapılamaz.',
      noModelLink: 'Ayarlar\'da bir model bağlayın',
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
      privacyNote: 'Modelin göreceği: {level}.',
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
  docs: {
    title: 'Belgeler',
    lead: 'Chart-er nasıl kullanılır, kendi kopyanız nasıl çalıştırılır ve kod üzerinde nasıl çalışılır.',
    sections: { guide: 'Chart-er\'i kullanmak', maintain: 'Chart-er\'i çalıştırmak ve değiştirmek' },
    sectionLead: {
      guide: 'Elinde bir tablo olan kişi için. Programlama bilgisi gerekmez.',
      maintain: 'Kendi kopyasını kuran ya da kod üzerinde çalışan kişi için.'
    },
    englishOnly: 'Bu sayfa yalnızca İngilizce olarak mevcut.',
    contents: 'Sayfalar',
    previous: 'Önceki',
    next: 'Sonraki',
    home: 'Tüm sayfalar'
  },
  status: { pending: 'Bekliyor', running: 'Çalışıyor', done: 'Tamam', failed: 'Başarısız' },
  errors: {
    network: 'Sunucuya ulaşılamadı.',
    unknown: 'Bir şeyler ters gitti.'
  }
};
