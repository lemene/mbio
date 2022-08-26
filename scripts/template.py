import sys
import traceback

'''创建代码模板'''




def tp_env(argv):
    '''创建添加特定路径到$PATH的脚本
    tp_env fname
'''

    s = '''TOOLPATH=~/b/tool


case $1 in
  bin)
    export PATH=${TOOLPATH}/bin:$PATH
    ;;
  quast)
    export PATH=${TOOLPATH}/quast-4.6.3:$PATH
    ;;
  gage)
    export PATH=${TOOLPATH}/gage-paper-validation:${TOOLPATH}/MUMmer3.23:$PATH
    ;;
  mecat)
    export PATH=${TOOLPATH}/MECAT/Linux-amd64/bin:$PATH
    ;;
  minimap2)
    export PATH=${TOOLPATH}/minimap2:$PATH
    ;;
  bwa)
    export PATH=${TOOLPATH}/bwa:$PATH
    ;;
  racon)
    export PATH=${TOOLPATH}/racon/build/bin/:$PATH
    ;;
  nanopolish)
    export PATH=${TOOLPATH}/nanopolish/:${TOOLPATH}/nanopolish/scripts:$PATH
    ;;
  samtools)
    export PATH=${TOOLPATH}/samtools/:$PATH
    ;;
  sratoolkit)
    export PATH=${TOOLPATH}/sratoolkit.2.9.1/bin:$PATH
    ;;
  racon)
    export PATH=${TOOLPATH}/racon/build/bin:$PATH
    ;;
  virtualenv)
    export PATH=${TOOLPATH}/virtualenv/build/lib.linux-x86_64-2.7:$PATH
    ;;
  canu)
    export PATH=${TOOLPATH}/canu/Linux-amd64/bin:$PATH
    ;;
  mecat)
    export PATH=${TOOLPATH}/MECAT/Linux-amd64/bin:$PATH
    ;;
  mummer4)
    export PATH=${TOOLPATH}/mummer-4.0.0beta2/:$PATH
    ;;
  gnuplot)
    export PATH=${TOOLPATH}/gnuplot-5.2.4/src:$PATH
    ;;
  java8)
    export PATH=${TOOLPATH}/java-se-8u40-ri/bin:$PATH
    export JAVA_HOME=${TOOLPATH}/java-se-8u40-ri
    ;;
  daligner)
    export PATH=${TOOLPATH}/DALIGNER:${TOOLPATH}/DEXTRACTOR:${PATH}
    export LD_LIBRARY_PATH=${TOOLPATH}/hdf5-1.8.20/src/.libs:${LD_LIBRARY_PATH}
    ;;
  *)
    echo "bad tool name"
    ;;
esac

'''
    try:
        fname = argv[0]
        open(fname,"w").write(s)
    except:
        traceback.print_exc()
        print("----------------")
        print(tp_env.__doc__)



if __name__ == '__main__':
    if len(sys.argv) > 1:
       locals()[sys.argv[1]](sys.argv[2:])
    else:
       for func in list(locals().keys()):
           if func.startswith("tp_"):
               print("%s: %s" % (func, locals()[func].__doc__.split("\n")[0]))