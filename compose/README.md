# 基于 Laradock 实现的本地快速部署环境、一键创建各版本镜像的脚本

# 使用方法：

## 本地开发：

> Step1: git clone xxxx项目，到你的PHP项目中

> Step2: python compose.py init 初始化配置

> Step3: vi ./laradock/.env 增加你希望安装的扩展（目前仅支持 workspace ，php-fpm的扩展）

> Step4: python compose.py start 运行（访问Http://yourhost）

## 打包镜像：

> Step1: python compose.py packup

> Step2: docker tag <imageId> repository:xxx

> Step3: docker push your images to your repository


# 为什么要做这个脚本？

> 本地使用 laradock 开发，能轻松的利用 docker 特性，但是，想将代码打包到 laradock 构建的 image 中，就很麻烦了。

> 尤其是当你本地有个环境，又要打包个仿真环境，又要打包个线上环境。如果没有一个脚本来处理，会很麻烦的。

> 并且，每个项目都需要进行一个配置，也很不方便。

> 这个脚本可以让你的项目，快速的打包到 docker 镜像中。

> 当然，目前仅支持 ngixn + php-fpm + redis。

> 对于 docker 还不很熟悉，所以数据库的创建，最好还是不要放在 docker 中：），你本地的开发，可以尽情的使用。
