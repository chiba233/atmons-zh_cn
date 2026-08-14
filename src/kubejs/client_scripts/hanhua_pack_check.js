// ATM10 汉化补丁「绿油油版」客户端资源包自检。
// 只读语言表与资源包列表，不下载、不写任何文件、不发网络请求。
//
// 为什么要做：最常见也最致命的一种「汉化坏了」，是玩家根本没在选项里启用资源包，
// 或者把它压在了别的包下面。这两种情况下玩家看到的是满屏英文，得出的结论却是
// 「这个汉化包是坏的」。README 的警告与配图只能拦住会看 README 的人。
//
// 两层判据，各管各的，都测**结果**而不是配置：
//
//   一、生效。资源包里埋了一个只有我们定义的键 atm10zhcn.pack.version
//       （assets/atm10zhcn/lang/zh_cn.json，值由构建脚本按发布版本现填）。
//       语言表是所有启用的包合并后的最终结果，所以查得到 = 包真的生效了。
//       读 options.txt 或看包在不在选中列表里都是查「配置」，在「名字对了但
//       文件坏了」这类情况下会给出错误的绿灯，所以不走那条路。
//       顺带还能抓到版本错配：查到的值与本脚本的版本不一致，说明玩家的
//       resourcepacks 里启用着旧版本的包（安装器只覆盖不删除，改过名的旧包
//       会一直留着）。
//
//   二、顺序。探针键只有我们定义，排第几都查得到，所以第一层测不出顺序——
//       这一点是实机验过的：把包拖到最低优先级，第一层照样报 ok。
//       既然第一层已经证明包加载了，这时候再去问 PackRepository 就是可靠的。
//       判据不是「必须排在最后一个」——那样玩家装个材质包放最上面就会被误报——
//       而是「排在我们之后（优先级更高）的包里，有没有人也提供 zh_cn 语言文件」，
//       只有那种包才会真的压住我们。正常安装下我们就是最后一个，这一步一个包
//       都不用打开，零开销。
//
// 判不准一律闭嘴。这跟构建期的闸正好相反：闸取不到基准要红，这里取不到判据必须
// 静默——给一个配置正常的玩家每次进游戏弹一次红字，比不做这个功能还糟。
//
// ⚠️ 遵守 hanhua_update_check.js 用两个发出去的版本换来的两条教训：
//    - **块里只许赋值，不许声明。** KubeJS 的 Rhino 会把 try/if/for 块内的 const
//      提升成函数作用域的 var，执行到声明那句抛 TypeError: redeclaration of var，
//      而且是运行时才抛、又被 catch 吞掉，表现成「什么都没发生」。所有声明写在
//      函数体顶层用 let。由 check.py 的 js-no-const-inside-block 守住。
//    - **Java.loadClass 只用字符串字面量，且类要过 kubejs.classfilter.txt。**
//      这里用到的四个类都在 `+ net.minecraft` 放行范围内（只有 net.minecraft.Util
//      被禁）。由 check_kubejs_classfilter.py 守住。
//
// 整份包在 IIFE 里：KubeJS 的 client_scripts 共用同一个全局作用域，顶层 const
// 撞名会让**整批脚本**加载失败（cb979c1 踩过一次）。
(function () {
  const PROBE_KEY = 'atm10zhcn.pack.version'
  const PROBE_NAMESPACE = 'atm10zhcn'
  const PACK_VERSION = '@@PATCHVER@@'
  const LANG_PATH = 'lang/zh_cn.json'
  // 进世界后等 3 秒再说话。loggedIn 在连接阶段就触发，世界真正加载完还要一会儿，
  // 立刻说会被进服刷屏冲掉；等 3 秒正好落在模组的进服提示后面。
  const DELAY_TICKS = 20 * 3

  let pending = 0
  let verdict = null
  let offenders = ''

  function say(line) {
    console.info('[ATM10 汉化] ' + line)
  }

  // ---------- 第一层：包生效了没有 ----------
  // 'ok' / 'missing' / 'mismatch:<包里写的版本>'；判不准返回 null
  function inspectLang() {
    let I18nClass = null
    let value = ''
    try {
      I18nClass = Java.loadClass('net.minecraft.client.resources.language.I18n')
    } catch (err) {
      say('自检取不到 I18n，跳过：' + err)
      return null
    }
    try {
      if (!I18nClass.exists(PROBE_KEY)) return 'missing'
      value = String(I18nClass.get(PROBE_KEY))
    } catch (err) {
      say('自检查表失败，跳过：' + err)
      return null
    }
    if (value === PACK_VERSION) return 'ok'
    return 'mismatch:' + value
  }

  // ---------- 第二层：有没有人压在我们上面 ----------
  // 'top' / 'blocked' / 'blocked:<玩家自己装的包名>'；判不准返回 null
  function inspectOrder() {
    let McClass = null
    let PackTypeClass = null
    let LocClass = null
    let repo = null
    let list = null
    let i = 0
    let j = 0
    let ourIndex = -1
    let pack = null
    let res = null
    let namespaces = null
    let ns = null
    let id = ''
    let names = []
    let blockers = 0
    let hit = false

    try {
      McClass = Java.loadClass('net.minecraft.client.Minecraft')
      PackTypeClass = Java.loadClass('net.minecraft.server.packs.PackType')
      LocClass = Java.loadClass('net.minecraft.resources.ResourceLocation')
      repo = McClass.getInstance().getResourcePackRepository()
      // 越靠后优先级越高。注意这个列表跟资源包界面看到的不是一回事：NeoForge 把
      // 每个模组自带的资源拆成独立的包，实测 ATM10 7.3 有 534 项，而界面里只有十几项。
      list = repo.getSelectedPacks().toArray()
    } catch (err) {
      say('顺序自检取不到包列表，跳过：' + err)
      return null
    }

    // 先定位我们自己：认命名空间，不认文件名——玩家把 zip 改了名也照样找得到
    for (i = 0; i < list.length; i++) {
      hit = false
      try {
        res = list[i].open()
        // close() 放 finally：open() 成功之后任何一步抛异常，句柄都得还回去，
        // 否则这个循环会在五百多个包上漏一串没关的 zip
        try {
          namespaces = res.getNamespaces(PackTypeClass.CLIENT_RESOURCES)
          hit = namespaces.contains(PROBE_NAMESPACE)
        } finally {
          res.close()
        }
      } catch (err) {
        hit = false
      }
      if (hit) {
        ourIndex = i
        break
      }
    }
    if (ourIndex < 0) {
      say('顺序自检：没在选中列表里认出自己，跳过')
      return null
    }
    say('顺序自检：我们排在 ' + (ourIndex + 1) + '/' + list.length)

    // 再看排在我们之后的包里，谁也提供 zh_cn。正常安装下这个循环一次都不进。
    for (i = ourIndex + 1; i < list.length; i++) {
      pack = list[i]
      hit = false
      try {
        res = pack.open()
        try {
          namespaces = res.getNamespaces(PackTypeClass.CLIENT_RESOURCES).toArray()
          for (j = 0; j < namespaces.length && !hit; j++) {
            ns = String(namespaces[j])
            if (res.getResource(PackTypeClass.CLIENT_RESOURCES,
                                LocClass.fromNamespaceAndPath(ns, LANG_PATH)) !== null) {
              hit = true
            }
          }
        } finally {
          res.close()
        }
      } catch (err) {
        say('顺序自检：读不动 ' + pack.getId() + '，跳过它（' + err + '）')
        hit = false
      }
      if (hit) {
        blockers++
        // 只点名玩家自己装的包（file/ 开头）。原版与模组自带资源确实也压着我们，
        // 但报出来没用：那个列表有五百多项而界面里只有十几项，报数字只会让玩家
        // 以为是 bug。不管压着的是什么，要做的动作都一样——把汉化包拖到最顶部。
        // 用 id 不用 getTitle()：「模组自带资源」那个包的标题是全部模组 jar 的
        // 文件名清单，几百行，会把聊天栏刷爆（实机踩过）。
        id = String(pack.getId())
        if (id.indexOf('file/') === 0 && names.length < 3) {
          names.push(id.substring('file/'.length))
        }
      }
    }
    if (blockers === 0) return 'top'
    if (names.length === 0) return 'blocked'
    return 'blocked:' + names.join('、')
  }

  function tell(result, blocked) {
    let player = Client.player
    let packed = ''
    if (!player) return

    if (result === 'missing') {
      player.tell(Text.red('[ATM10 汉化] ')
        .append(Text.yellow('汉化资源包没有生效，游戏里绝大部分文本仍然是英文。')))
      player.tell(Text.gray('  打开 ')
        .append(Text.white('选项 → 资源包'))
        .append(Text.gray('，把 '))
        .append(Text.white('ATM10汉化包'))
        .append(Text.gray(' 拖到右侧「已选」一列的'))
        .append(Text.white('最顶部'))
        .append(Text.gray('。')))
      return
    }

    if (result === 'order') {
      player.tell(Text.gold('[ATM10 汉化] ')
        .append(Text.yellow('汉化资源包被压在下面了，部分名字会显示成别的译法。')))
      if (blocked !== '') {
        player.tell(Text.gray('  你自己装的 ')
          .append(Text.white(blocked))
          .append(Text.gray(' 排在它上面。')))
      }
      player.tell(Text.gray('  打开 ')
        .append(Text.white('选项 → 资源包'))
        .append(Text.gray('，把 '))
        .append(Text.white('ATM10汉化包'))
        .append(Text.gray(' 拖到「已选」一列的'))
        .append(Text.white('最顶部'))
        .append(Text.gray('。')))
      return
    }

    packed = result.substring('mismatch:'.length)
    player.tell(Text.red('[ATM10 汉化] ')
      .append(Text.yellow('资源包版本与汉化本体对不上：包是 ' + packed
        + '，本体是 ' + PACK_VERSION + '。')))
    player.tell(Text.gray('  多半是旧版本的包还留在 resourcepacks 里且被启用着，'
      + '重新跑一遍安装器即可。'))
  }

  ClientEvents.loggedIn(event => {
    let lang = null
    let order = null
    pending = 0
    verdict = null
    offenders = ''

    lang = inspectLang()
    say('资源包自检：' + lang)
    if (lang === null) return
    if (lang !== 'ok') {
      verdict = lang
      pending = DELAY_TICKS
      return
    }

    // 包确实生效了，这时候问顺序才有意义
    order = inspectOrder()
    say('顺序自检结论：' + (order === null ? '判不准' : order))
    if (order === null || order === 'top') return
    verdict = 'order'
    offenders = ''
    if (order.indexOf('blocked:') === 0) offenders = order.substring('blocked:'.length)
    pending = DELAY_TICKS
  })

  ClientEvents.tick(event => {
    if (pending <= 0) return
    pending--
    if (pending === 0) tell(verdict, offenders)
  })
})()
