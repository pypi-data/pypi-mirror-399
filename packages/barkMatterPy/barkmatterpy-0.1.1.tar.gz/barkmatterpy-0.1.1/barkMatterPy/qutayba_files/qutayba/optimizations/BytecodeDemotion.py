#     Copyright 2025, QutaYba, nasr2python@gmail.com find license text at end of file


""" Demotion of compiled modules to bytecode modules.

"""

import marshal

from JACK.BytecodeCaching import writeImportedModulesNamesToCache
from JACK.Bytecodes import compileSourceToBytecode
from JACK.freezer.ImportDetection import detectEarlyImports
from JACK.importing.ImportCache import (
    isImportedModuleByName,
    replaceImportedModule,
)
from JACK.ModuleRegistry import replaceRootModule
from JACK.nodes.ModuleNodes import makeUncompiledPythonModule
from JACK.Options import isShowProgress, isStandaloneMode
from JACK.plugins.Plugins import (
    Plugins,
    isTriggerModule,
    replaceTriggerModule,
)
from JACK.Tracing import inclusion_logger
from JACK.utils.FileOperations import getNormalizedPath


def demoteSourceCodeToBytecode(module_name, source_code, filename):
    if isStandaloneMode():
        filename = module_name.asPath() + ".py"

    bytecode = compileSourceToBytecode(source_code, filename)

    bytecode = Plugins.onFrozenModuleBytecode(
        module_name=module_name, is_package=False, bytecode=bytecode
    )

    return marshal.dumps(bytecode)


def demoteCompiledModuleToBytecode(module):
    """Demote a compiled module to uncompiled (bytecode)."""

    full_name = module.getFullName()
    filename = module.getCompileTimeFilename()

    if isShowProgress():
        inclusion_logger.info(
            "Demoting module '%s' to bytecode from '%s'."
            % (full_name.asString(), filename)
        )

    source_code = module.getSourceCode()

    bytecode = demoteSourceCodeToBytecode(
        module_name=full_name, source_code=source_code, filename=filename
    )

    uncompiled_module = makeUncompiledPythonModule(
        module_name=full_name,
        reason=module.reason,
        filename=getNormalizedPath(filename),
        bytecode=bytecode,
        is_package=module.isCompiledPythonPackage(),
        technical=full_name in detectEarlyImports(),
    )

    used_modules = module.getUsedModules()
    uncompiled_module.setUsedModules(used_modules)

    distribution_names = module.getUsedDistributions()
    uncompiled_module.setUsedDistributions(distribution_names)

    module.finalize()

    if isImportedModuleByName(full_name):
        replaceImportedModule(old=module, new=uncompiled_module)
    replaceRootModule(old=module, new=uncompiled_module)

    if isTriggerModule(module):
        replaceTriggerModule(old=module, new=uncompiled_module)

    writeImportedModulesNamesToCache(
        module_name=full_name,
        source_code=source_code,
        used_modules=used_modules,
        distribution_names=distribution_names,
    )



